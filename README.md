# Serverless Media Processing Pipeline

A fully automated, event-driven architecture for image processing and content moderation on AWS. This project demonstrates a "Serverless-First" approach, utilizing **Infrastructure as Code (Terraform)** for deployment and **AWS Lambda Powertools** for advanced observability.

---

## 🏗 Architecture

The pipeline follows an event-driven workflow:

1.  **Ingestion:** User uploads an image (`.jpg`) to the **Input S3 Bucket**.
2.  **Trigger:** An S3 Event Notification invokes the **AWS Lambda** function.
3.  **Processing:**
    * **Resize:** The image is processed in-memory using the **Pillow** library.
    * **Moderation:** The image is analyzed by **AWS Rekognition** to detect unsafe content (e.g., explicit nudity or violence).
4.  **Decision Logic:**
    * ✅ **Safe:** Resized image is saved to the **Output S3 Bucket**.
    * ❌ **Unsafe:** Processing stops, image is rejected, and an alert is sent via **Amazon SNS**.
5.  **Persistence:** Metadata (processing status, labels, dimensions, request ID) is stored in **Amazon DynamoDB**.
6.  **Observability:** Logs, Metrics, and Traces (X-Ray) are collected via **AWS Lambda Powertools**.

---

## 🚀 Features

* **Serverless Architecture:** Zero server management using AWS Lambda.
* **Infrastructure as Code (IaC):** Entire infrastructure provisioned via **Terraform**.
* **AI Content Moderation:** Automated safety checks using AWS Rekognition.
* **Operational Excellence:** Structured JSON logging, custom metrics, and distributed tracing with AWS X-Ray.
* **Security First:** IAM roles follow the **Principle of Least Privilege**.
* **Event-Driven:** Asynchronous processing triggered by S3 state changes.

---

## 🛠 Tech Stack

* **Cloud Provider:** AWS (S3, Lambda, DynamoDB, Rekognition, SNS, IAM, CloudWatch, X-Ray)
* **IaC:** Terraform
* **Language:** Python 3.9
* **Libraries:** `boto3`, `Pillow`, `aws-lambda-powertools`, `aws-xray-sdk`

---

## 📂 Project Structure

```text
.
├── src/
│   ├── app.py              # Main Lambda logic
│   └── requirements.txt    # Python dependencies
├── terraform/
│   ├── main.tf             # Infrastructure definition
├── .gitignore              # Ignored build artifacts
└── README.md               # Project documentation
```

## ⚙️ Setup & Deployment

### Prerequisites
* AWS Account & CLI configured locally.
* Terraform installed.
* Python 3.9+ installed.

### 1. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/serverless-media-pipeline.git](https://github.com/YOUR_USERNAME/serverless-media-pipeline.git)
cd serverless-media-pipeline
```

### 2. Install Dependencies (Crucial Step)
Since AWS Lambda runs on Linux (x86_64) and libraries like Pillow (listed in requirements.txt) rely on C-extensions, we must install platform-specific binaries. If you are developing on macOS or Windows, a standard pip install will result in errors on Lambda.

### Run this command in the project root:

```bash
pip3 install -r src/requirements.txt -t src/ \
--platform manylinux2014_x86_64 \
--only-binary=:all: \
--upgrade \
--python-version 3.9
```

### 3. Deploy Infrastructure
Initialize and apply the Terraform configuration.

```bash
cd terraform
terraform init
terraform apply
```