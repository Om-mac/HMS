#!/bin/bash

#############################################
# HMS - AWS Setup (Simplified - Docker Redis)
# Uses Docker Redis on EC2 instead of ElastiCache
#############################################

set -e

REGION="ap-south-1"
PROJECT_NAME="hms"
DB_NAME="hms_db"
DB_USER="hms_admin"
DB_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)
DJANGO_SECRET_KEY=$(openssl rand -base64 50 | tr -dc 'a-zA-Z0-9' | head -c 50)
AES_ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
S3_BUCKET_NAME="vakverse-hms-medical-files"
EC2_KEY_NAME="hms-key-pair"
EC2_INSTANCE_TYPE="t3.micro"

export AWS_DEFAULT_REGION=$REGION

echo "============================================"
echo "  HMS AWS Setup - Simplified"
echo "  Region: $REGION (Mumbai, India)"
echo "  (Uses Docker Redis on EC2)"
echo "============================================"

# Get existing resources
echo ""
echo "🔍 Finding existing resources..."

VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=$PROJECT_NAME-vpc" --query 'Vpcs[0].VpcId' --output text)
echo "   VPC: $VPC_ID"

SUBNET_PUBLIC_1=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=$PROJECT_NAME-public-1" --query 'Subnets[0].SubnetId' --output text)
echo "   Public Subnet 1: $SUBNET_PUBLIC_1"

EC2_SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$PROJECT_NAME-ec2-sg" --query 'SecurityGroups[0].GroupId' --output text)
echo "   EC2 Security Group: $EC2_SG_ID"

#############################################
# Check RDS Status
#############################################
echo ""
echo "🗄️ Checking RDS PostgreSQL Database..."

RDS_STATUS=$(aws rds describe-db-instances \
    --db-instance-identifier "$PROJECT_NAME-db" \
    --query 'DBInstances[0].DBInstanceStatus' \
    --output text 2>/dev/null || echo "not_found")

if [[ "$RDS_STATUS" == "not_found" ]]; then
    echo "   ❌ RDS not found. Please run the main setup script first."
    exit 1
else
    echo "   ℹ️ RDS Status: $RDS_STATUS"
fi

#############################################
# Skip ElastiCache - Use Docker Redis
#############################################
echo ""
echo "⚡ Step 5: Skipping ElastiCache (will use Docker Redis on EC2)"
echo "   ℹ️ Redis will run in Docker on the EC2 instance"

#############################################
# 6. Create IAM Role for EC2
#############################################
echo ""
echo "👤 Step 6: Setting up IAM Role for EC2..."

ROLE_EXISTS=$(aws iam get-role --role-name "$PROJECT_NAME-ec2-role" 2>/dev/null && echo "exists" || echo "not_found")

if [[ "$ROLE_EXISTS" == "not_found" ]]; then
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
        --assume-role-policy-document file:///tmp/ec2-trust-policy.json 2>/dev/null || true

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
        --policy-document file:///tmp/s3-policy.json 2>/dev/null || true

    echo "   ✅ IAM Role created"
else
    echo "   ℹ️ IAM Role already exists"
fi

# Create Instance Profile
PROFILE_EXISTS=$(aws iam get-instance-profile --instance-profile-name "$PROJECT_NAME-ec2-profile" 2>/dev/null && echo "exists" || echo "not_found")

if [[ "$PROFILE_EXISTS" == "not_found" ]]; then
    aws iam create-instance-profile --instance-profile-name "$PROJECT_NAME-ec2-profile" 2>/dev/null || true
    sleep 2
    aws iam add-role-to-instance-profile \
        --instance-profile-name "$PROJECT_NAME-ec2-profile" \
        --role-name "$PROJECT_NAME-ec2-role" 2>/dev/null || true
    echo "   ✅ Instance Profile created"
    sleep 10
else
    echo "   ℹ️ Instance Profile already exists"
fi

#############################################
# 7. Create EC2 Key Pair
#############################################
echo ""
echo "🔑 Step 7: Setting up EC2 Key Pair..."

KEY_EXISTS=$(aws ec2 describe-key-pairs --key-names $EC2_KEY_NAME 2>/dev/null && echo "exists" || echo "not_found")

if [[ "$KEY_EXISTS" == "not_found" ]]; then
    aws ec2 create-key-pair \
        --key-name $EC2_KEY_NAME \
        --query 'KeyMaterial' \
        --output text > /tmp/$EC2_KEY_NAME.pem
    chmod 400 /tmp/$EC2_KEY_NAME.pem
    cp /tmp/$EC2_KEY_NAME.pem ~/Desktop/$EC2_KEY_NAME.pem 2>/dev/null || true
    echo "   ✅ Key Pair created and saved to ~/Desktop/$EC2_KEY_NAME.pem"
else
    echo "   ℹ️ Key Pair already exists"
fi

#############################################
# 8. Create EC2 Instance
#############################################
echo ""
echo "🖥️ Step 8: Creating EC2 Instance..."

INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$PROJECT_NAME-server" "Name=instance-state-name,Values=running,pending" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text 2>/dev/null)

if [[ "$INSTANCE_ID" == "None" ]] || [[ -z "$INSTANCE_ID" ]]; then
    # Get latest Ubuntu 22.04 AMI
    AMI_ID=$(aws ec2 describe-images \
        --owners 099720109477 \
        --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
        --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
        --output text)
    echo "   Using AMI: $AMI_ID"

    cat > /tmp/user-data.sh << 'USERDATA'
#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
apt-get install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx git

# Start Docker
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Create app directory
mkdir -p /opt/hms
chown ubuntu:ubuntu /opt/hms

# Signal completion
echo "EC2 setup complete at $(date)" > /home/ubuntu/setup-complete.txt
USERDATA

    # Try with instance profile first, fall back to without
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $EC2_INSTANCE_TYPE \
        --key-name $EC2_KEY_NAME \
        --security-group-ids $EC2_SG_ID \
        --subnet-id $SUBNET_PUBLIC_1 \
        --user-data file:///tmp/user-data.sh \
        --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20,"VolumeType":"gp2"}}]' \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME-server}]" \
        --query 'Instances[0].InstanceId' \
        --output text 2>/dev/null) || \
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $EC2_INSTANCE_TYPE \
        --key-name $EC2_KEY_NAME \
        --security-group-ids $EC2_SG_ID \
        --subnet-id $SUBNET_PUBLIC_1 \
        --user-data file:///tmp/user-data.sh \
        --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20,"VolumeType":"gp2"}}]' \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME-server}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo "   ⏳ EC2 instance launching: $INSTANCE_ID"
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    echo "   ✅ EC2 Instance running!"
else
    echo "   ℹ️ EC2 Instance already exists: $INSTANCE_ID"
fi

#############################################
# 9. Create/Get Elastic IP
#############################################
echo ""
echo "🌍 Step 9: Setting up Elastic IP..."

EXISTING_EIP=$(aws ec2 describe-addresses \
    --filters "Name=tag:Name,Values=$PROJECT_NAME-eip" \
    --query 'Addresses[0].AllocationId' \
    --output text 2>/dev/null)

if [[ "$EXISTING_EIP" == "None" ]] || [[ -z "$EXISTING_EIP" ]]; then
    ALLOCATION_ID=$(aws ec2 allocate-address \
        --domain vpc \
        --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=Name,Value=$PROJECT_NAME-eip}]" \
        --query 'AllocationId' \
        --output text)
    echo "   ✅ Elastic IP allocated"
else
    ALLOCATION_ID=$EXISTING_EIP
    echo "   ℹ️ Using existing Elastic IP"
fi

# Associate with instance
aws ec2 associate-address \
    --instance-id $INSTANCE_ID \
    --allocation-id $ALLOCATION_ID 2>/dev/null || true

ELASTIC_IP=$(aws ec2 describe-addresses \
    --allocation-ids $ALLOCATION_ID \
    --query 'Addresses[0].PublicIp' \
    --output text)

echo "   ✅ Elastic IP: $ELASTIC_IP"

#############################################
# Wait for RDS
#############################################
echo ""
echo "⏳ Waiting for RDS to be available..."
echo "   (This takes 5-10 minutes, please wait...)"

aws rds wait db-instance-available --db-instance-identifier "$PROJECT_NAME-db" 2>/dev/null || true

RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier "$PROJECT_NAME-db" \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text 2>/dev/null || echo "pending")

echo "   ✅ RDS Endpoint: $RDS_ENDPOINT"

#############################################
# OUTPUT SUMMARY
#############################################
echo ""
echo "============================================"
echo "  🎉 AWS INFRASTRUCTURE SETUP COMPLETE!"
echo "============================================"
echo ""
echo "🖥️  EC2 INSTANCE:"
echo "    Instance ID: $INSTANCE_ID"
echo "    Elastic IP: $ELASTIC_IP"
echo "    SSH Command: ssh -i ~/Desktop/$EC2_KEY_NAME.pem ubuntu@$ELASTIC_IP"
echo ""
echo "🗄️  DATABASE (RDS PostgreSQL):"
echo "    Endpoint: $RDS_ENDPOINT"
echo "    Database: $DB_NAME"
echo "    Username: $DB_USER"
echo "    Password: $DB_PASSWORD"
echo ""
echo "⚡ REDIS:"
echo "    Will run in Docker on EC2"
echo "    URL: redis://localhost:6379/0"
echo ""
echo "📦 S3 BUCKET:"
echo "    Bucket: $S3_BUCKET_NAME"
echo "    Region: $REGION"
echo ""
echo "🔐 APPLICATION SECRETS:"
echo "    Django Secret Key: $DJANGO_SECRET_KEY"
echo "    AES Encryption Key: $AES_ENCRYPTION_KEY"
echo ""
echo "🌐 DNS CONFIGURATION:"
echo "    Point www.vakverse.com → $ELASTIC_IP"
echo "    Point vakverse.com → $ELASTIC_IP"
echo ""
echo "============================================"
echo ""
echo "📝 NEXT STEPS:"
echo ""
echo "1. SSH into your server:"
echo "   ssh -i ~/Desktop/$EC2_KEY_NAME.pem ubuntu@$ELASTIC_IP"
echo ""
echo "2. Clone your repo on the server:"
echo "   git clone https://github.com/Om-mac/HMS.git /opt/hms"
echo ""
echo "3. Update your domain DNS (Route 53 or your registrar):"
echo "   Add A record: vakverse.com → $ELASTIC_IP"
echo "   Add A record: www.vakverse.com → $ELASTIC_IP"
echo ""
echo "============================================"

# Save credentials
cat > ~/Desktop/hms-credentials.txt << EOF
============================================
HMS AWS CREDENTIALS - $(date)
KEEP THIS FILE SECURE!
============================================

EC2 SERVER:
  Instance ID: $INSTANCE_ID
  Elastic IP: $ELASTIC_IP
  SSH Command: ssh -i ~/Desktop/$EC2_KEY_NAME.pem ubuntu@$ELASTIC_IP

DATABASE (RDS PostgreSQL):
  Endpoint: $RDS_ENDPOINT
  Port: 5432
  Database: $DB_NAME
  Username: $DB_USER
  Password: $DB_PASSWORD
  Connection URL: postgres://$DB_USER:$DB_PASSWORD@$RDS_ENDPOINT:5432/$DB_NAME

REDIS:
  Will run in Docker on EC2
  URL: redis://localhost:6379/0

S3:
  Bucket: $S3_BUCKET_NAME
  Region: $REGION

APPLICATION SECRETS:
  Django Secret Key: $DJANGO_SECRET_KEY
  AES Encryption Key: $AES_ENCRYPTION_KEY

DNS SETUP:
  Point these domains to: $ELASTIC_IP
  - vakverse.com
  - www.vakverse.com

SSH KEY FILE:
  ~/Desktop/$EC2_KEY_NAME.pem

DEPLOYMENT COMMANDS:
  1. SSH into server:
     ssh -i ~/Desktop/$EC2_KEY_NAME.pem ubuntu@$ELASTIC_IP

  2. Clone and deploy:
     git clone https://github.com/Om-mac/HMS.git /opt/hms
     cd /opt/hms
     docker compose up -d
EOF

echo "📁 Credentials saved to: ~/Desktop/hms-credentials.txt"
echo ""
