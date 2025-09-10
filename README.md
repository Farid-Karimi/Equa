# Equa: AI-Powered Burnout Coach

Equa is a comprehensive system for burnout detection that uses machine learning and a large language model (LLM) to provide a proactive approach to workplace wellness. By analyzing key employee metrics, Equa predicts an individual's burnout risk and offers personalized, AI-driven coaching to support mental well-being.

The project combines robust predictive modeling with empathetic AI guidance to offer a scalable and accessible tool for early burnout detection and intervention.

## Key Features

* **Predictive Modeling:** Utilizes a Gradient Boosting Regressor model to accurately predict an individual's burnout score based on professional and personal metrics.
* **Risk Categorization:** Classifies individuals into Low, Moderate, and High-risk categories to provide a clear understanding of their current well-being.
* **AI-Powered Coaching:** Integrates with the Mistral-7B large language model to deliver personalized, empathetic advice based on the user's predicted burnout risk.
* **Interactive Conversation:** The AI coach supports natural, conversational follow-up questions, allowing for a more dynamic and helpful user experience.

## Dataset

This project was developed using the "Are Your Employees Burning Out?" dataset, which is sourced from a 2008 survey. The dataset is publicly available through the Harvard Dataverse.

[Link to Dataset](https://dataverse.harvard.edu/file.xhtml?fileId=11074732&version=1.0&toolType=PREVIEW)

## How It Works

The system's core is a Gradient Boosting Regressor model trained on a real-world dataset of employee metrics. This model demonstrated high predictive accuracy, achieving an R-squared ($R^2$) score of 0.90 on the test set. A feature importance analysis revealed that `Mental Fatigue Score` is the most significant predictor of burnout.

The predicted score is then passed to an AI wellness coach powered by the Mistral-7B model via the OpenRouter API. This coach generates a personalized plan and interacts with the user. The entire system is deployed as a user-friendly web application using Streamlit.