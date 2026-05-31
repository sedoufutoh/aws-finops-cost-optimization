# FinOps Cost Optimization Engine

**AWS Serverless | Automated EC2 Scheduling | EventBridge CRON | Cost Anomaly Detection**

---

## 1. Problem Statement

An Alberta tech company runs EC2 development instances 24/7. Developers leave resources 
running after hours and on weekends — wasting $800–2,000/month on idle compute. No one 
is monitoring the bill until month-end when the damage is done.

---

## 2. Cloud Solution

A fully automated FinOps cost optimization engine that:
- Shuts down all Development-tagged EC2 instances at 7 PM Mountain Time every weekday
- Starts them back up at 7 AM Mountain Time every weekday
- Sends email notifications on every shutdown and startup event
- Monitors monthly spend with AWS Budgets alerts at 80% and 100% threshold
- Detects unexpected cost spikes using AWS Cost Anomaly Detection (ML-based)

Result: Up to 65% reduction in dev environment compute costs with zero manual effort.

---

## 3. Architecture

    EventBridge Schedule (CRON — 7 PM MT weekdays)
            ↓
    Lambda — ShutdownDevResources
    - Finds all EC2 instances tagged Environment=Development + state=running
    - Stops all matching instances
    - Publishes shutdown report to SNS
            ↓
    SNS — FinOpsAlerts
    - Email notification to admin with list of stopped instances

    EventBridge Schedule (CRON — 7 AM MT weekdays)
            ↓
    Lambda — StartDevResources
    - Finds all EC2 instances tagged Environment=Development + state=stopped
    - Starts all matching instances
    - Publishes startup report to SNS
            ↓
    AWS Budgets — Monthly threshold alerts (80% + 100%)
    Cost Anomaly Detection — ML-based spike detection

---

## 4. AWS Services Used

| Service | Role |
|---|---|
| EventBridge Scheduler | Two CRON schedules: shutdown (1:00 AM UTC) + startup (2:00 PM UTC) weekdays |
| Lambda x2 | shutdown_dev.py + start_dev.py — boto3 EC2 stop/start API calls |
| EC2 | Development instances tagged Environment=Development |
| SNS | FinOpsAlerts topic — email notifications on every event |
| AWS Budgets | Monthly cost threshold alerts at 80% and 100% |
| Cost Anomaly Detection | Free ML-based spend anomaly monitor for all AWS services |
| IAM | FinOpsLambdaRole — EC2 + SNS + CloudWatch permissions |
| CloudWatch | Lambda execution logs |

---

## 5. Key Concepts Demonstrated

- **Resource tagging strategy** — Environment=Development tag as the automation control plane
- **EventBridge CRON scheduling** — UTC math for Mountain Time conversion
- **boto3 tag-based filtering** — describe_instances with Filters for tag + state
- **AWS Budgets** — cost threshold alerts at multiple percentages
- **Cost Anomaly Detection** — ML monitor types and sensitivity settings
- **IAM least privilege** — scoped to EC2 stop/start + SNS publish only
- **FinOps Optimize stage** — automated rightsizing through scheduling

---

## 6. Business Value

- Up to 65% reduction on dev environment compute costs
- 108 out of 168 weekly hours saved (weekday nights + full weekends)
- Zero manual effort after initial setup
- Every CTO asks why the AWS bill is high — this project shows exactly how to fix it
- Demonstrates FinOps maturity: Inform (Budgets + Anomaly Detection) + Optimize (scheduling)
- $0/month infrastructure cost for the automation itself

---

## 7. CRON Expression Explained

| Schedule | CRON | UTC Time | Mountain Time |
|---|---|---|---|
| Shutdown | 0 1 ? * 2-6 * | 1:00 AM UTC | 7:00 PM MT (UTC-6) |
| Startup | 0 14 ? * 2-6 * | 2:00 PM UTC | 8:00 AM MT (UTC-6) |

Days 2-6 = Monday through Friday. Weekends are skipped — instances stay stopped 
from Friday 7 PM to Monday 7 AM, capturing maximum savings.

---

## 8. Deployment Guide

### Prerequisites
- AWS Account
- EC2 instances tagged with Key=Environment,
