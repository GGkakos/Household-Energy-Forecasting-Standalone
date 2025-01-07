# Household Energy Forecasting  

---

> ### Note: Standalone Repository – Maintained by Georgios Gkakos
> This repository represents the completed and now standalone version of a collaborative project originally built by:
> 
> [Marij Qureshi](https://github.com/MarijQ), [Georgios Gkakos](https://github.com/GGkakos), [Het Suhagiya](https://github.com/HetSuhagiya)
> 
> As of **29/12/2024**, the original repository has been archived. This standalone version is now maintained by **Georgios Gkakos** for future updates and improvements.

---


## Table of Contents

1. [Introduction](#introduction)  
2. [Tech Stack](#tech-stack)   
3. [Running the Code](#running-the-code)  
4. [Data Preparation](#data-preparation)
5. [Machine Learning / Deep Learning Models](#machine-learning--deep-learning-models) 
6. [Results](#results)  
7. [Overall Insights and Reflections](#overall-insights-and-reflections)    
8. [Team and Contact](#team-and-contact)
9. [License](#license)

--- 

## Introduction  

The goal of our project is to predict how much energy people might use in the future for electricity and gas. By looking at past energy usage, weather data, and other factors, we want to help people better understand their energy habits. This can make it easier to plan, save money, and use resources more wisely.  

In this project, we’ve worked as a team to build a tool that uses data and machine learning to make these predictions.  

Key activities:  
- **Data Preparation:** Cleaning, preprocessing, and feature engineering.  
- **Model Implementation:** Experimenting with and fine-tuning machine learning models.  
- **Evaluation and Analysis:** Interpreting results and refining predictions.  
- **Visualization and Documentation:** Creating visualizations and maintaining the project documentation.  

---

## Tech Stack  

### ***ML Models:***  

We explored and implemented several models to predict energy consumption:  
- **ARIMA and SARIMA:** For capturing patterns and seasonality in the energy usage data.  
- **LSTM:** A deep learning approach that helps uncover complex patterns and trends over time.  
- **Prophet:** A model well-suited for time series data, helping us make reliable and interpretable predictions.  

### ***Libraries:***  

The project leverages Python as the primary programming language, alongside essential libraries such as Pandas, NumPy, Matplotlib, TensorFlow, and Facebook’s Prophet. These tools allowed us to preprocess data, train models, and visualize results effectively.  

---

## Running the Code 
This project is implemented in a Jupyter Notebook. To run the code, simply follow these steps:

1. Open the Jupyter Notebook by running:

    ```bash
    jupyter notebook
    ```

2. Open the notebook file (`*.ipynb`) in the Jupyter interface.

3. Run the entire script by selecting **Run All** from the "Cell" menu. The notebook will execute all the code, including model training and evaluation.

> **Please see the Jupyter Notebook for the full analysis and report write-up - the summary below highlights methodology, key results and insights.**

---

## Data Preparation  

The IDEAL Household Energy Dataset provided information on energy usage across 255 homes, including electricity and gas, as well as metadata on household characteristics, sensors, and weather conditions. Preparing this data was essential to ensure its accuracy and usability for our project.  

### ***Data Source:***  

The dataset was sourced from the [IDEAL Household Energy Dataset](https://datashare.ed.ac.uk/handle/10283/3647). It includes time-series data from sensors installed in homes, along with metadata such as home layouts, appliance types, and environmental factors.  

### ***Merging Datasets:***

 - The dataset included individually zipped CSV files for each sensor in every home, with data split across multiple files.
 - We merged all sensor data into a single CSV per home by aligning and matching timestamps across the sensors.
 - After merging, we renamed columns for consistency and clarity while trimming any unnecessary or redundant features.

### ***Data Cleaning:***  

- For most features, missing values were handled using forward and backward filling, ensuring continuity in time-series data.  
- Gas data had the highest proportion of missing values. In these cases, missing values were replaced with 0, assuming no gas usage during those periods, as outlined in the dataset documentation.
- Gaps in weather data were filled using Fourier Series, complemented by the residuals of the Fourier analysis to capture realistic temperature variability throughout the year.  

### ***Feature Engineering:***  

To enhance the dataset for modeling, additional features were created:    
- **Weather Data Integration:**  To align with energy consumption data, we generated hourly timestamps for weather data using a sine function, with maximum temperatures timed to peak at 4 PM.
- **Metadata Integration:** Merged external metadata for individual homes, such as household characteristics, location data, and boiler type, onto the primary consumption dataset for enriched multi-dimensional analyses.

These screenshots demonstrate an example of weather data imputation and simulation of hourly timestamps:
- **Original Weather Data for Fife:**
  
![image](https://github.com/user-attachments/assets/40f894d3-2431-4b0f-a071-18f961783250)

- **Imputed Weather Data:**
  
![image](https://github.com/user-attachments/assets/6b7c4686-13e9-4e50-80df-6bfff129edf5)

- **Simulation of Hourly Weather Data used in Models:**
  
![image](https://github.com/user-attachments/assets/24d19655-d089-4c1f-9e67-8631b94743df)


---

## Machine Learning / Deep Learning Models  

In this project, we used several machine learning models, each chosen for their ability to handle time series data and make accurate predictions about energy usage.  

### ***ARIMA (AutoRegressive Integrated Moving Average):***  

ARIMA is a statistical model that helps us understand and predict future values based on past data. It’s useful for time series data like energy consumption, where the past behavior of the data can help us forecast future trends. 

We trained two seperate models, one for electricity and one for gas consumption - for each ARIMA only used historical values of the corresponding target variable to predict future values. 

### ***SARIMAX (Seasonal ARIMA and Exogenous variables):***  

SARIMAX builds on ARIMA but includes the ability to handle seasonal patterns in the data as well as exogenous variables. Since energy usage can often be affected by seasonal factors (like weather), SARIMA helps capture these regular fluctuations to improve predictions.

These models built on the ARIMA autoregressive prediction but added in weather data (simulated hourly temperatures) as well as household metadata.

### ***LSTM (Long Short-Term Memory):***  

LSTM is a type of deep learning model designed for sequential data. It’s particularly good at learning long-term dependencies and capturing complex patterns over time. This model is used to detect intricate patterns in energy usage that might not be easily visible with traditional methods.

These models maintained the same explanatory variables (weather/metadata) and target variables (electricity/gas) as SARIMAX for consistency. A simple version of the model was trained on a single household, and a another model sequentially re-trained on 20 randomly-chosen households to reduce overfitting.

### ***Prophet:***  

Prophet is an open-source model developed by Facebook for forecasting time series data. It’s easy to use and works well with data that has strong seasonal effects, like energy consumption. We used it because it’s reliable and interpretable, which makes it a good choice for predicting future energy use.

### ***Model evaluation:***  

To evaluate the performance and generalisability of our models across households, we employed cross-validation by testing trained models on 5 randomly allocated unseen homes. The average evaluation metric score was taken.

We used Root Mean Square Error (RMSE) as the primary evaluation metric. RMSE penalizes large prediction errors more than smaller ones, providing a more robust assessment of accuracy. A lower RMSE value indicates better model performance.

Note that the accuracy of predictions are dependent on the choice of households for training and test data (particularly for single-home models) - this can be mitigated by implementing hyperparameter tuning and repeated testing.

---

## Results  

The results of our energy consumption prediction models highlight the performance of each approach for forecasting electricity and gas usage. Below is a summary of the evaluation results using RMSE (Root Mean Square Error) as the metric:  

### **Evaluation Results (Electricity):**  

### **Electricity Consumption:**  
| Model             | RMSE       |
|-------------------|------------|
| ARIMA             | 4579       |
| SARIMAX           | 1231       |
| LSTM Single       | 990        |
| LSTM Sequential   | 1178       |
| Prophet           | 2482       |

**Example fitted electricity model (ARIMA, home 316):**  
![image](https://github.com/user-attachments/assets/3a4e3498-8b8a-465d-af0d-2e40b150f5a6)

### Analysis:

**ARIMA:**
ARIMA performed poorly with an RMSE of 4579 due to its inability to incorporate seasonality and nonlinear trends, limiting its effectiveness on this dataset.

**SARIMAX:**
With an RMSE of 1231, SARIMAX provided better results. Its inclusion of seasonal effects and external predictors like weather data helped it capture short-term fluctuations and periodic trends.

**LSTM (Single):**
This model performed the best, achieving an RMSE of 990. Its ability to model long-term dependencies and nonlinear patterns in sequential data made it the most accurate.

**LSTM (Sequential):**
Sequential LSTM, trained on data from multiple households, achieved an RMSE of 1178. Its broader training scope reduced accuracy slightly but provided better generalisation across households.

**Prophet:**
Prophet had an RMSE of 2482. While effective at capturing seasonality, it struggled with more complex variable interactions and nonlinear trends, reducing its overall accuracy.

### Key Takeaways:
- Clear patterns in electricity data: Stable trends and seasonality favored models with temporal sensitivity like LSTM and SARIMAX.
- Advanced modeling wins: LSTMs excelled by capturing both nonlinearities and long-term dependencies in the data.
SARIMAX’s robustness: Simple yet effective, SARIMAX benefited from incorporating seasonal and external predictors.
- Limitations of ARIMA and Prophet: ARIMA failed due to its simplicity, while Prophet struggled with complex relationships despite handling seasonality well.
- Generalisation tradeoff: Sequential LSTM offered more generalized predictions, while single LSTM excelled at single-household accuracy.

### **Evaluation Results (Gas):** 

### **Gas Consumption:**  
| Model             | RMSE       |
|-------------------|------------|
| ARIMA             | 2936       |
| SARIMAX           | 2937       |
| LSTM Single       | 5266       |
| LSTM Sequential   | 2984       |
| Prophet           | 12197      |

**Example fitted gas model (ARIMA, home 316):**  
![image](https://github.com/user-attachments/assets/bb349be9-59e9-4a10-924f-423e72ea5d1f)

### Analysis:

**ARIMA:**
ARIMA performed best with an RMSE of 2936. Its statistical simplicity worked well for the relatively short-term dependencies in the gas data. However, it struggled with irregular usage patterns and sparse data.

**SARIMAX:**
SARIMAX recorded a nearly identical RMSE of 2937, with no notable advantage over ARIMA. The seasonal components and exogenous variables provided limited extra predictive power, likely due to the inconsistencies in gas patterns.

**LSTM (Sequential):**
Sequential LSTM had an RMSE of 2984, slightly worse than ARIMA and SARIMAX. While LSTMs generally excel at modeling complex relationships, the high number of missing values combined with irregular consumption data limited its accuracy compared to simpler methods.

**LSTM (Single):**
This model performed poorly with an RMSE of 5266, the highest among models other than Prophet. The lack of sufficient training data for a single household likely caused overfitting or failure to generalize.

**Prophet:**
Prophet had the worst performance with an RMSE of 12197. It struggled with the sparse and irregular nature of the gas data, likely due to its reliance on clear seasonality and trends.

### Key Takeaways:

- Gas predictions are difficult: Irregular and sparse data, combined with missing values imputed as zero, made gas consumption harder to predict than electricity.
- Limitations of LSTMs: Both single and sequential LSTMs underperformed due to irregular patterns and insufficient data for effective deep-learning modeling.
- Prophet’s constraints: Prophet, designed for strong seasonal trends, struggled with the highly variable and inconsistent nature of the gas consumption data.
- Temperature impact: Weather features like temperature played a key role, with colder weather correlating to higher gas usage, but this signal wasn’t enough to boost complex models in this case.

---

## Overall Insights and Reflections:
- Electricity predictions were easier and more accurate: Stable patterns and clear seasonality allowed models like LSTM and SARIMAX to perform well, with LSTM (Single) being the most effective at capturing complex temporal dependencies. However, this outperformance may be due to random chance (variation between households and random sampling)
- Gas predictions were more challenging: Irregular usage patterns, sparse data, and imputed missing values significantly hindered model performance, particularly for LSTM. Additionally, choosing to exclude all households with >50% missing values for gas and imputing the remainder as zeros may have exacerbated this.
- Prophet struggled with variability: Its design for datasets with strong seasonality and trends limited its ability to handle the irregular and inconsistent patterns seen in gas consumption. This model was also not able to benefit from additional explanatory variables such as weather context or metadata.
- Data quality and feature engineering are critical: The results highlight the need for better handling of missing data and tailored imputation approaches (particularly for excessive missing values).
- Alternative approaches: In order to mitigate the model underperformance due to significant variation in energy consumption between households - an alternative approach could first group homes into usage bands and then train sequentially on each band. For deep learning models such as LSTM, this could be further augmented by additional datasets.

---

## Team and Contact

- **Marij Qureshi**: MEng Aeronautical Engineering (Imperial), MSc Data Science (Brunel), ex-EY Parthenon
- **Georgios Gkakos**: MSc Data Science (Brunel), BSc Economics (AUTH)
- **Het Suhagiya**: MSc Data Science (Brunel), BSc Information Technology 

For questions, feel free to reach out via GitHub issues or email any of us.

---

## License  

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
