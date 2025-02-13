# ========================================
# Libraries and Global Configuration
# ========================================

import os
import random
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
import tensorflow as tf
import matplotlib.pyplot as plt

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TensorFlow warnings
tf.config.optimizer.set_jit(True)  # Enable JIT compilation for GPUs if available

# Global directories and settings
INPUT_DIR = r"./ind-homes-final"
OUTPUT_DIR = r"./Marij/charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# ========================================
# Utility Functions
# ========================================

def preprocess_data(df):
    """
    Preprocesses input files: handle missing data, ensure timestamps,
    encode categorical variables, and select key fields.
    
    Returns the DataFrame with dummy-encoded columns (if any object dtype).
    """
    # Ensure 'timestamp' is in datetime format and set as index
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
    
    # Reindex to ensure consistent hourly frequency
    if len(df.index) > 0:
        df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="h"))
    
    # Fill missing values for 'elec' and 'gas'
    if "elec" in df.columns:
        df["elec"] = df["elec"].interpolate(method="linear").bfill().ffill()
    if "gas" in df.columns:
        df["gas"] = df["gas"].fillna(0)

    # Identify categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # Encode categorical variables using one-hot encoding
    df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    # Fill any remaining missing values with zeros
    df.fillna(0, inplace=True)

    return df

def evaluate_model(y_true, y_pred):
    """Compute RMSE for predictions."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return rmse if np.isfinite(rmse) else None

def random_household_selection(num_files=1, exclude=[]):
    """Randomly selects `num_files` household files, excluding the specified ones."""
    all_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".csv")]
    available_files = [f for f in all_files if f not in exclude]
    return random.sample(available_files, num_files)

# ========================================
# ARIMA Model
# ========================================

def fit_arima(df, target_col):
    """Train ARIMA model using fixed order (1, 0, 1) for the target variable."""
    order = (1, 0, 1)
    model = ARIMA(df[target_col], order=order)
    fitted_model = model.fit()
    return fitted_model

def evaluate_arima():
    """Train and evaluate ARIMA on a single random household, test on 5 random households."""
    train_file = random_household_selection(1)[0]
    df_train = preprocess_data(pd.read_csv(os.path.join(INPUT_DIR, train_file)))
    train_cols = df_train.columns

    test_files = random_household_selection(5, exclude=[train_file])

    # Store RMSE values separately for elec and gas
    rmse_dict = {"elec": [], "gas": []}

    for target in ["elec", "gas"]:
        if target not in df_train.columns:
            continue

        arima_model = fit_arima(df_train, target)
        for test_file in test_files:
            df_test = preprocess_data(pd.read_csv(os.path.join(INPUT_DIR, test_file)))
            df_test = df_test.reindex(columns=train_cols, fill_value=0)

            if target not in df_test.columns:
                continue

            try:
                forecast = arima_model.forecast(steps=len(df_test))
                rmse = np.sqrt(mean_squared_error(df_test[target], forecast))
                if np.isfinite(rmse):
                    rmse_dict[target].append(rmse)
            except:
                pass

    # Convert list of RMSEs to mean per target
    for t in rmse_dict:
        rmse_dict[t] = np.mean(rmse_dict[t]) if rmse_dict[t] else None
    return rmse_dict

# ========================================
# SARIMAX Model
# ========================================

def fit_sarimax(df, target_col):
    """Train SARIMAX model using extra covariates (all other columns)."""
    exogenous_columns = df.columns.difference([target_col])
    exog = df[exogenous_columns]

    # Ensure exogenous variables are numeric and no missing
    exog = exog.select_dtypes(include=[np.number])
    exog.fillna(0, inplace=True)

    model = SARIMAX(df[target_col], exog=exog, order=(1, 0, 1))
    fitted_model = model.fit(disp=False)
    return fitted_model

def evaluate_sarimax():
    """Train and evaluate SARIMAX on a single random household, test on 5 random households."""
    train_file = random_household_selection(1)[0]
    df_train = preprocess_data(pd.read_csv(os.path.join(INPUT_DIR, train_file)))
    train_cols = df_train.columns

    test_files = random_household_selection(5, exclude=[train_file])
    rmse_dict = {"elec": [], "gas": []}

    for target in ["elec", "gas"]:
        if target not in df_train.columns:
            continue

        sarimax_model = fit_sarimax(df_train, target_col=target)
        for test_file in test_files:
            df_test = preprocess_data(pd.read_csv(os.path.join(INPUT_DIR, test_file)))
            df_test = df_test.reindex(columns=train_cols, fill_value=0)

            if target not in df_test.columns:
                continue

            exog_test = df_test[df_test.columns.difference([target])]
            exog_test = exog_test.select_dtypes(include=[np.number]).fillna(0)

            try:
                forecast = sarimax_model.forecast(steps=len(df_test), exog=exog_test)
                forecast = forecast[:len(df_test[target])]
                rmse = np.sqrt(mean_squared_error(df_test[target], forecast))
                if np.isfinite(rmse):
                    rmse_dict[target].append(rmse)
            except Exception as e:
                print(f"Error during SARIMAX evaluation for {test_file}: {e}")

    for t in rmse_dict:
        rmse_dict[t] = np.mean(rmse_dict[t]) if rmse_dict[t] else None
    return rmse_dict

# ========================================
# LSTM Single Household
# ========================================

def fit_lstm_single(df, target_col):
    """Train LSTM model on one household for a single target variable."""
    # Drop rows where target is missing
    df = df.dropna(subset=[target_col])
    
    # Separate features/target
    data = df.drop(columns=[target_col]).values
    target = df[target_col].values

    # Scale features and target
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    data_scaled = scaler_X.fit_transform(data)
    target_scaled = scaler_y.fit_transform(target.reshape(-1, 1))

    # Create sequences
    sequence_len = 24  # Use previous 24 hours as input
    X, y = [], []
    for i in range(sequence_len, len(data_scaled)):
        X.append(data_scaled[i - sequence_len:i])
        y.append(target_scaled[i])
    X, y = np.array(X), np.array(y)

    # Build LSTM model
    model = Sequential([
        Input(shape=(X.shape[1], X.shape[2])),
        LSTM(50, return_sequences=True),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=10, batch_size=32, verbose=0)

    return model, scaler_X, scaler_y

def evaluate_lstm_single():
    """Train and evaluate LSTM on a single random household, test on 5 random households."""
    train_file = random_household_selection(1)[0]
    df_train = preprocess_data(pd.read_csv(os.path.join(INPUT_DIR, train_file)))
    train_cols = df_train.columns

    test_files = random_household_selection(5, exclude=[train_file])
    rmse_dict = {"elec": [], "gas": []}

    for target in ["elec", "gas"]:
        if target not in df_train.columns:
            continue

        lstm_model, scaler_X, scaler_y = fit_lstm_single(df_train, target)

        for test_file in test_files:
            df_test = preprocess_data(pd.read_csv(os.path.join(INPUT_DIR, test_file)))
            df_test = df_test.reindex(columns=train_cols, fill_value=0)

            if target not in df_test.columns:
                continue
            df_test = df_test.dropna(subset=[target])

            data_test = df_test.drop(columns=[target]).values
            target_test = df_test[target].values

            data_test_scaled = scaler_X.transform(data_test)

            # Create sequences
            sequence_len = 24
            X_test = []
            for i in range(sequence_len, len(data_test_scaled)):
                X_test.append(data_test_scaled[i - sequence_len:i])
            X_test = np.array(X_test)
            y_test = target_test[sequence_len:]

            y_pred_scaled = lstm_model.predict(X_test)
            y_pred = scaler_y.inverse_transform(y_pred_scaled)

            rmse = np.sqrt(mean_squared_error(y_test, y_pred.flatten()))
            if np.isfinite(rmse):
                rmse_dict[target].append(rmse)

    for t in rmse_dict:
        rmse_dict[t] = np.mean(rmse_dict[t]) if rmse_dict[t] else None
    return rmse_dict

# ========================================
# LSTM Sequential Training
# ========================================

def fit_lstm_sequential(train_dfs, target_col):
    """
    Train LSTM model sequentially on multiple DataFrames (already preprocessed & reindexed).
    Returns the final model and the scalers.
    """
    model, scaler_X, scaler_y = None, None, None
    sequence_len = 24

    for idx, df in enumerate(train_dfs):
        df = df.dropna(subset=[target_col])
        data = df.drop(columns=[target_col]).values
        target = df[target_col].values

        # Initialize scalers if first iteration
        if model is None:
            # First file dictates the shape and initializes everything
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()

            data_scaled = scaler_X.fit_transform(data)
            target_scaled = scaler_y.fit_transform(target.reshape(-1, 1))

            # Build model
            model = Sequential([
                Input(shape=(sequence_len, data_scaled.shape[1])),
                LSTM(50, return_sequences=True),
                LSTM(50),
                Dense(1)
            ])
            model.compile(optimizer="adam", loss="mse")
        else:
            # For subsequent files, transform with existing scalers
            data_scaled = scaler_X.transform(data)
            target_scaled = scaler_y.transform(target.reshape(-1, 1))

        # Create sequences
        X, y = [], []
        for i in range(sequence_len, len(data_scaled)):
            X.append(data_scaled[i - sequence_len:i])
            y.append(target_scaled[i])
        X, y = np.array(X), np.array(y)

        # Train the model incrementally
        model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    return model, scaler_X, scaler_y

def evaluate_lstm_sequential():
    """
    Train LSTM sequentially on 5 random households, then evaluate on another 5,
    returning separate RMSE for elec and gas.
    """
    train_files = random_household_selection(20)
    test_files = random_household_selection(5, exclude=train_files)

    train_dfs = []
    union_train_cols = set()

    # Preprocess each train file, accumulate the union of columns
    for f in train_files:
        df_temp = preprocess_data(pd.read_csv(os.path.join(INPUT_DIR, f)))
        train_dfs.append(df_temp)
        union_train_cols = union_train_cols.union(df_temp.columns)
    union_train_cols = list(union_train_cols)

    # Reindex each train df to the union of columns
    for idx, df_temp in enumerate(train_dfs):
        train_dfs[idx] = df_temp.reindex(columns=union_train_cols, fill_value=0)

    rmse_dict = {"elec": [], "gas": []}

    for target in ["elec", "gas"]:
        if target not in union_train_cols:
            continue

        lstm_model, scaler_X, scaler_y = fit_lstm_sequential(train_dfs, target)

        # Evaluate on test files
        for test_file in test_files:
            df_test = preprocess_data(pd.read_csv(os.path.join(INPUT_DIR, test_file)))
            df_test = df_test.reindex(columns=union_train_cols, fill_value=0)

            if target not in df_test.columns:
                continue
            df_test = df_test.dropna(subset=[target])

            data_test = df_test.drop(columns=[target]).values
            target_test = df_test[target].values
            data_test_scaled = scaler_X.transform(data_test)

            sequence_len = 24
            X_test = []
            for i in range(sequence_len, len(data_test_scaled)):
                X_test.append(data_test_scaled[i - sequence_len:i])
            X_test = np.array(X_test)
            y_true = target_test[sequence_len:]

            y_pred_scaled = lstm_model.predict(X_test)
            y_pred = scaler_y.inverse_transform(y_pred_scaled)

            rmse = np.sqrt(mean_squared_error(y_true, y_pred.flatten()))
            if np.isfinite(rmse):
                rmse_dict[target].append(rmse)

    for t in rmse_dict:
        rmse_dict[t] = np.mean(rmse_dict[t]) if rmse_dict[t] else None
    return rmse_dict

# ========================================
# Main Execution
# ========================================

if __name__ == "__main__":
    print("Evaluating ARIMA Model...")
    arima_results = evaluate_arima()

    print("Evaluating SARIMAX Model...")
    sarimax_results = evaluate_sarimax()

    print("Evaluating Single-Household LSTM...")
    lstm_single_results = evaluate_lstm_single()

    print("Evaluating LSTM Sequential Training...")
    lstm_seq_results = evaluate_lstm_sequential()

    # Consolidate results
    results = {
        "ARIMA": arima_results,
        "SARIMAX": sarimax_results,
        "LSTM Single": lstm_single_results,
        "LSTM Sequential": lstm_seq_results
    }

    # Display results
    print("\nEvaluation Results (RMSE for Elec and Gas):")
    for model, rmse_dict in results.items():
        elec_rmse = rmse_dict.get("elec", "N/A")
        gas_rmse = rmse_dict.get("gas", "N/A")
        print(f"{model} -> Elec RMSE: {elec_rmse:.3f} | Gas RMSE: {gas_rmse:.3f}")
