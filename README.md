# 📷 FastAPI Image Upload Service on AWS

This project is a simple **FastAPI** application deployed on AWS.  
It allows users to upload images, save their metadata in a database (Amazon RDS), store the image files in Amazon S3, and send notifications via Amazon SNS to subscribers when new images are uploaded.

---

## 🛠 Architecture Overview

- **FastAPI** app running on EC2 instances behind an **Auto Scaling Group** and **Elastic Load Balancer** (ALB).
- **Amazon RDS** for relational database storage (metadata persistence).
- **Amazon S3** for storing uploaded images.
- **Amazon SNS** for publishing upload notifications to subscribers.
- **AWS Lambda** functions for:
  - Data consistency checks.
  - Sending notifications upon successful upload.
- **AWS CodePipeline** for CI/CD, pulling source code from **GitHub** and deploying updates automatically.

---

## ⚙️ Components

| Component        | Service                                 |
|:-----------------|:----------------------------------------|
| **Frontend/API**  | FastAPI                                 |
| **Compute**       | EC2 (T2 instances) with Auto Scaling Group |
| **Load Balancing**| Application Load Balancer              |
| **Database**      | Amazon RDS (inside a private subnet)    |
| **Storage**       | Amazon S3                               |
| **Notification**  | Amazon SNS                              |
| **Serverless**    | AWS Lambda (data consistency, SNS notification) |
| **CI/CD**         | AWS CodePipeline (source: GitHub)       |
| **Networking**    | VPC with public and private subnets across 2 AZs |

---

## 📄 Flow

1. **User uploads an image** through the FastAPI endpoint.
2. **FastAPI application**:
   - Saves the image file to **Amazon S3**.
   - Saves the metadata (e.g., filename, URL, timestamp) to **Amazon RDS**.
   - Sends a notification message to **Amazon SNS**.
3. **AWS Lambda** ensures data consistency.
4. **SNS Subscribers** receive notifications (e.g., Email, SMS).
5. **CodePipeline** handles automatic deployment from **GitHub** to AWS.

---

## 📦 Deployment Process

1. **Push code** to GitHub repository.
2. **AWS CodePipeline** detects changes and triggers a build and deployment.
3. **Updated FastAPI application** is deployed to the EC2 instances automatically.

