#!/bin/bash

#############################################
# HMS - Healthcare Management System
# AWS Infrastructure Setup Script
# Region: ap-south-1 (Mumbai, India)
# Domain: www.vakverse.com
#############################################

set -e

# Configuration
REGION="ap-south-1"
PROJECT_NAME="hms"
DOMAIN="vakverse.com"
DB_NAME="hms_db"
DB_USER="hms_admin"
DB_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)
DJANGO_SECRET_KEY=$(openssl rand -base64 50 | tr -dc 'a-zA-Z0-9' | head -c 50)
AES_ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
S3_BUCKET_NAME="vakverse-hms-medical-files"
EC2_KEY_NAME="hms-key-pair"
EC2_INSTANCE_TYPE="t3.medium"

echo "============================================"
echo "  HMS AWS Infrastructure Setup"
echo "  Region: $REGION (Mumbai, India)"
echo "============================================"
echo ""

# Set default region
aws configure set default.region $REGION
export AWS_DEFAULT_REGION=$REGION

echo "📍 Setting region to $REGION..."

#############################################
# 1. Create VPC and Networking
#############################################
echo ""
echo "🌐 Step 1: Creating VPC and Networking..."

# Create VPC
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$PROJECT_NAME-vpc}]" \
    --query 'Vpc.VpcId' \
    --output text)
echo "   ✅ VPC created: $VPC_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=$PROJECT_NAME-igw}]" \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
echo "   ✅ Internet Gateway created: $IGW_ID"

# Create Public Subnet 1
SUBNET_PUBLIC_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone ${REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public-1}]" \
    --query 'Subnet.SubnetId' \
    --output text)
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_PUBLIC_1 --map-public-ip-on-launch
echo "   ✅ Public Subnet 1: $SUBNET_PUBLIC_1"

# Create Public Subnet 2
SUBNET_PUBLIC_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone ${REGION}b \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-public-2}]" \
    --query 'Subnet.SubnetId' \
    --output text)
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_PUBLIC_2 --map-public-ip-on-launch
echo "   ✅ Public Subnet 2: $SUBNET_PUBLIC_2"

# Create Private Subnet 1 (for RDS)
SUBNET_PRIVATE_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.3.0/24 \
    --availability-zone ${REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-private-1}]" \
    --query 'Subnet.SubnetId' \
    --output text)
echo "   ✅ Private Subnet 1: $SUBNET_PRIVATE_1"

# Create Private Subnet 2 (for RDS)
SUBNET_PRIVATE_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.4.0/24 \
    --availability-zone ${REGION}b \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-private-2}]" \
    --query 'Subnet.SubnetId' \
    --output text)
echo "   ✅ Private Subnet 2: $SUBNET_PRIVATE_2"

# Create Route Table
RTB_ID=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$PROJECT_NAME-rtb}]" \
    --query 'RouteTable.RouteTableId' \
    --output text)
aws ec2 create-route --route-table-id $RTB_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --subnet-id $SUBNET_PUBLIC_1 --route-table-id $RTB_ID
aws ec2 associate-route-table --subnet-id $SUBNET_PUBLIC_2 --route-table-id $RTB_ID
echo "   ✅ Route Table created: $RTB_ID"

#############################################
# 2. Create Security Groups
#############################################
echo ""
echo "🔒 Step 2: Creating Security Groups..."

# EC2 Security Group
EC2_SG_ID=$(aws ec2 create-security-group \
    --group-name "$PROJECT_NAME-ec2-sg" \
    --description "Security group for HMS EC2 instance" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Allow SSH (22), HTTP (80), HTTPS (443), Custom ports
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 3000 --cidr 0.0.0.0/0
echo "   ✅ EC2 Security Group: $EC2_SG_ID"

# RDS Security Group
RDS_SG_ID=$(aws ec2 create-security-group \
    --group-name "$PROJECT_NAME-rds-sg" \
    --description "Security group for HMS RDS instance" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Allow PostgreSQL from EC2 only
aws ec2 authorize-security-group-ingress --group-id $RDS_SG_ID --protocol tcp --port 5432 --source-group $EC2_SG_ID
echo "   ✅ RDS Security Group: $RDS_SG_ID"

# Redis Security Group
REDIS_SG_ID=$(aws ec2 create-security-group \
    --group-name "$PROJECT_NAME-redis-sg" \
    --description "Security group for HMS Redis" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)
aws ec2 authorize-security-group-ingress --group-id $REDIS_SG_ID --protocol tcp --port 6379 --source-group $EC2_SG_ID
echo "   ✅ Redis Security Group: $REDIS_SG_ID"

#############################################
# 3. Create S3 Bucket
#############################################
echo ""
echo "📦 Step 3: Creating S3 Bucket..."

# Create S3 bucket with encryption
aws s3api create-bucket \
    --bucket $S3_BUCKET_NAME \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket $S3_BUCKET_NAME \
    --versioning-configuration Status=Enabled

# Enable server-side encryption
aws s3api put-bucket-encryption \
    --bucket $S3_BUCKET_NAME \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

# Block public access
aws s3api put-public-access-block \
    --bucket $S3_BUCKET_NAME \
    --public-access-block-configuration '{
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }'

echo "   ✅ S3 Bucket created: $S3_BUCKET_NAME"

#############################################
# 4. Create RDS PostgreSQL
#############################################
echo ""
echo "🗄️ Step 4: Creating RDS PostgreSQL Database..."

# Create DB Subnet Group
aws rds create-db-subnet-group \
    --db-subnet-group-name "$PROJECT_NAME-db-subnet-group" \
    --db-subnet-group-description "Subnet group for HMS RDS" \
    --subnet-ids $SUBNET_PRIVATE_1 $SUBNET_PRIVATE_2

# Create RDS Instance (Free Tier Compatible)
aws rds create-db-instance \
    --db-instance-identifier "$PROJECT_NAME-db" \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version "16.1" \
    --master-username $DB_USER \
    --master-user-password $DB_PASSWORD \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids $RDS_SG_ID \
    --db-subnet-group-name "$PROJECT_NAME-db-subnet-group" \
    --db-name $DB_NAME \
    --backup-retention-period 1 \
    --no-publicly-accessible \
    --no-deletion-protection \
    --no-multi-az \
    --tags Key=Name,Value="$PROJECT_NAME-db"

echo "   ⏳ RDS instance is being created (takes 5-10 minutes)..."
echo "   ✅ RDS Instance: $PROJECT_NAME-db"

#############################################
# 5. Create ElastiCache Redis
#############################################
echo ""
echo "⚡ Step 5: Creating ElastiCache Redis..."

# Create ElastiCache Subnet Group
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name "$PROJECT_NAME-redis-subnet-group" \
    --cache-subnet-group-description "Subnet group for HMS Redis" \
    --subnet-ids $SUBNET_PRIVATE_1 $SUBNET_PRIVATE_2

# Create Redis Cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id "$PROJECT_NAME-redis" \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1 \
    --cache-subnet-group-name "$PROJECT_NAME-redis-subnet-group" \
    --security-group-ids $REDIS_SG_ID \
    --tags Key=Name,Value="$PROJECT_NAME-redis"

echo "   ⏳ Redis cluster is being created..."
echo "   ✅ Redis Cluster: $PROJECT_NAME-redis"

#############################################
# 6. Create IAM Role for EC2
#############################################
echo ""
echo "👤 Step 6: Creating IAM Role for EC2..."

# Create IAM Role
cat > /tmp/ec2-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role \
    --role-name "$PROJECT_NAME-ec2-role" \
    --assume-role-policy-document file:///tmp/ec2-trust-policy.json

# Create S3 Policy
cat > /tmp/s3-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::$S3_BUCKET_NAME",
                "arn:aws:s3:::$S3_BUCKET_NAME/*"
            ]
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name "$PROJECT_NAME-ec2-role" \
    --policy-name "$PROJECT_NAME-s3-policy" \
    --policy-document file:///tmp/s3-policy.json

# Attach CloudWatch policy for logs
aws iam attach-role-policy \
    --role-name "$PROJECT_NAME-ec2-role" \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

# Create Instance Profile
aws iam create-instance-profile --instance-profile-name "$PROJECT_NAME-ec2-profile"
aws iam add-role-to-instance-profile \
    --instance-profile-name "$PROJECT_NAME-ec2-profile" \
    --role-name "$PROJECT_NAME-ec2-role"

echo "   ✅ IAM Role created: $PROJECT_NAME-ec2-role"

# Wait for instance profile to be ready
sleep 10

#############################################
# 7. Create EC2 Key Pair
#############################################
echo ""
echo "🔑 Step 7: Creating EC2 Key Pair..."

aws ec2 create-key-pair \
    --key-name $EC2_KEY_NAME \
    --query 'KeyMaterial' \
    --output text > /tmp/$EC2_KEY_NAME.pem

chmod 400 /tmp/$EC2_KEY_NAME.pem
echo "   ✅ Key Pair created: $EC2_KEY_NAME"
echo "   📁 Private key saved to: /tmp/$EC2_KEY_NAME.pem"

#############################################
# 8. Create EC2 Instance
#############################################
echo ""
echo "🖥️ Step 8: Creating EC2 Instance..."

# Get latest Ubuntu 22.04 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

# Create User Data Script
cat > /tmp/user-data.sh << 'USERDATA'
#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx git

# Start Docker
systemctl start docker
systemctl enable docker

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Create app directory
mkdir -p /opt/hms
chown ubuntu:ubuntu /opt/hms

echo "EC2 setup complete!" > /home/ubuntu/setup-complete.txt
USERDATA

# Launch EC2 Instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $EC2_INSTANCE_TYPE \
    --key-name $EC2_KEY_NAME \
    --security-group-ids $EC2_SG_ID \
    --subnet-id $SUBNET_PUBLIC_1 \
    --iam-instance-profile Name="$PROJECT_NAME-ec2-profile" \
    --user-data file:///tmp/user-data.sh \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":30,"VolumeType":"gp3","Encrypted":true}}]' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME-server}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "   ⏳ EC2 instance is launching..."
echo "   ✅ EC2 Instance: $INSTANCE_ID"

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get Public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "   ✅ Public IP: $PUBLIC_IP"

#############################################
# 9. Create Elastic IP
#############################################
echo ""
echo "🌍 Step 9: Creating Elastic IP..."

ALLOCATION_ID=$(aws ec2 allocate-address \
    --domain vpc \
    --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=Name,Value=$PROJECT_NAME-eip}]" \
    --query 'AllocationId' \
    --output text)

aws ec2 associate-address \
    --instance-id $INSTANCE_ID \
    --allocation-id $ALLOCATION_ID

ELASTIC_IP=$(aws ec2 describe-addresses \
    --allocation-ids $ALLOCATION_ID \
    --query 'Addresses[0].PublicIp' \
    --output text)

echo "   ✅ Elastic IP: $ELASTIC_IP"

#############################################
# 10. Store Secrets in AWS Secrets Manager
#############################################
echo ""
echo "🔐 Step 10: Storing Secrets in AWS Secrets Manager..."

aws secretsmanager create-secret \
    --name "$PROJECT_NAME/production" \
    --description "HMS Production Secrets" \
    --secret-string "{
        \"DJANGO_SECRET_KEY\": \"$DJANGO_SECRET_KEY\",
        \"AES_ENCRYPTION_KEY\": \"$AES_ENCRYPTION_KEY\",
        \"DB_NAME\": \"$DB_NAME\",
        \"DB_USER\": \"$DB_USER\",
        \"DB_PASSWORD\": \"$DB_PASSWORD\",
        \"S3_BUCKET\": \"$S3_BUCKET_NAME\"
    }"

echo "   ✅ Secrets stored in AWS Secrets Manager"

#############################################
# 11. Create IAM User for Application
#############################################
echo ""
echo "👤 Step 11: Creating IAM User for Application..."

aws iam create-user --user-name "$PROJECT_NAME-app-user"

# Create access key
ACCESS_KEY_OUTPUT=$(aws iam create-access-key --user-name "$PROJECT_NAME-app-user")
AWS_ACCESS_KEY_ID=$(echo $ACCESS_KEY_OUTPUT | jq -r '.AccessKey.AccessKeyId')
AWS_SECRET_ACCESS_KEY=$(echo $ACCESS_KEY_OUTPUT | jq -r '.AccessKey.SecretAccessKey')

# Attach S3 policy to user
cat > /tmp/app-user-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$S3_BUCKET_NAME",
                "arn:aws:s3:::$S3_BUCKET_NAME/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam put-user-policy \
    --user-name "$PROJECT_NAME-app-user" \
    --policy-name "$PROJECT_NAME-app-policy" \
    --policy-document file:///tmp/app-user-policy.json

echo "   ✅ IAM User created: $PROJECT_NAME-app-user"

#############################################
# Wait for RDS and get endpoint
#############################################
echo ""
echo "⏳ Waiting for RDS to be available (this takes 5-10 minutes)..."
aws rds wait db-instance-available --db-instance-identifier "$PROJECT_NAME-db"

RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier "$PROJECT_NAME-db" \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

echo "   ✅ RDS Endpoint: $RDS_ENDPOINT"

#############################################
# Wait for Redis and get endpoint
#############################################
echo ""
echo "⏳ Waiting for Redis to be available..."
aws elasticache wait cache-cluster-available --cache-cluster-id "$PROJECT_NAME-redis"

REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
    --cache-cluster-id "$PROJECT_NAME-redis" \
    --show-cache-node-info \
    --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
    --output text)

echo "   ✅ Redis Endpoint: $REDIS_ENDPOINT"

#############################################
# OUTPUT SUMMARY
#############################################
echo ""
echo "============================================"
echo "  🎉 AWS INFRASTRUCTURE SETUP COMPLETE!"
echo "============================================"
echo ""
echo "📋 SAVE THESE CREDENTIALS SECURELY:"
echo "--------------------------------------------"
echo ""
echo "🖥️  EC2 INSTANCE:"
echo "    Instance ID: $INSTANCE_ID"
echo "    Elastic IP: $ELASTIC_IP"
echo "    SSH Command: ssh -i /tmp/$EC2_KEY_NAME.pem ubuntu@$ELASTIC_IP"
echo ""
echo "🗄️  DATABASE (RDS PostgreSQL):"
echo "    Endpoint: $RDS_ENDPOINT"
echo "    Database: $DB_NAME"
echo "    Username: $DB_USER"
echo "    Password: $DB_PASSWORD"
echo "    Connection URL: postgres://$DB_USER:$DB_PASSWORD@$RDS_ENDPOINT:5432/$DB_NAME"
echo ""
echo "⚡ REDIS (ElastiCache):"
echo "    Endpoint: $REDIS_ENDPOINT"
echo "    URL: redis://$REDIS_ENDPOINT:6379/0"
echo ""
echo "📦 S3 BUCKET:"
echo "    Bucket Name: $S3_BUCKET_NAME"
echo "    Region: $REGION"
echo ""
echo "🔑 AWS CREDENTIALS (for application):"
echo "    Access Key ID: $AWS_ACCESS_KEY_ID"
echo "    Secret Access Key: $AWS_SECRET_ACCESS_KEY"
echo ""
echo "🔐 APPLICATION SECRETS:"
echo "    Django Secret Key: $DJANGO_SECRET_KEY"
echo "    AES Encryption Key: $AES_ENCRYPTION_KEY"
echo ""
echo "🌐 DNS CONFIGURATION:"
echo "    Point www.vakverse.com → $ELASTIC_IP"
echo "    Point vakverse.com → $ELASTIC_IP"
echo ""
echo "🔑 SSH KEY:"
echo "    Download from: /tmp/$EC2_KEY_NAME.pem"
echo "    Run: cat /tmp/$EC2_KEY_NAME.pem"
echo ""
echo "============================================"
echo ""
echo "📝 NEXT STEPS:"
echo "1. Copy the SSH key from CloudShell:"
echo "   cat /tmp/$EC2_KEY_NAME.pem"
echo ""
echo "2. Update your domain DNS:"
echo "   Add A record: www.vakverse.com → $ELASTIC_IP"
echo "   Add A record: vakverse.com → $ELASTIC_IP"
echo ""
echo "3. SSH into your server:"
echo "   ssh -i hms-key-pair.pem ubuntu@$ELASTIC_IP"
echo ""
echo "============================================"

# Save all info to a file
cat > /tmp/hms-credentials.txt << EOF
============================================
HMS AWS CREDENTIALS - KEEP SECURE!
Generated: $(date)
============================================

EC2 INSTANCE:
  Instance ID: $INSTANCE_ID
  Elastic IP: $ELASTIC_IP
  SSH: ssh -i hms-key-pair.pem ubuntu@$ELASTIC_IP

DATABASE (RDS):
  Endpoint: $RDS_ENDPOINT
  Database: $DB_NAME
  Username: $DB_USER
  Password: $DB_PASSWORD

REDIS:
  Endpoint: $REDIS_ENDPOINT

S3:
  Bucket: $S3_BUCKET_NAME
  Region: $REGION

AWS CREDENTIALS:
  Access Key ID: $AWS_ACCESS_KEY_ID
  Secret Access Key: $AWS_SECRET_ACCESS_KEY

APPLICATION SECRETS:
  Django Secret Key: $DJANGO_SECRET_KEY
  AES Encryption Key: $AES_ENCRYPTION_KEY

VPC:
  VPC ID: $VPC_ID
  Public Subnet 1: $SUBNET_PUBLIC_1
  Public Subnet 2: $SUBNET_PUBLIC_2
  EC2 Security Group: $EC2_SG_ID
  RDS Security Group: $RDS_SG_ID

DNS (Point these to $ELASTIC_IP):
  www.vakverse.com
  vakverse.com
EOF

echo "📁 All credentials saved to: /tmp/hms-credentials.txt"
echo "   Run: cat /tmp/hms-credentials.txt"
echo ""
