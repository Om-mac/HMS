#!/bin/bash

#############################################
# HMS - Continue AWS Setup (Free Tier Compatible)
# Picks up from where the first script stopped
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
echo "  HMS AWS Setup - Continuation"
echo "  Region: $REGION (Mumbai, India)"
echo "============================================"

# Get existing resources
echo ""
echo "🔍 Finding existing resources..."

VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=$PROJECT_NAME-vpc" --query 'Vpcs[0].VpcId' --output text)
echo "   VPC: $VPC_ID"

SUBNET_PUBLIC_1=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=$PROJECT_NAME-public-1" --query 'Subnets[0].SubnetId' --output text)
echo "   Public Subnet 1: $SUBNET_PUBLIC_1"

SUBNET_PRIVATE_1=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=$PROJECT_NAME-private-1" --query 'Subnets[0].SubnetId' --output text)
SUBNET_PRIVATE_2=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=$PROJECT_NAME-private-2" --query 'Subnets[0].SubnetId' --output text)

EC2_SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$PROJECT_NAME-ec2-sg" --query 'SecurityGroups[0].GroupId' --output text)
echo "   EC2 Security Group: $EC2_SG_ID"

RDS_SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$PROJECT_NAME-rds-sg" --query 'SecurityGroups[0].GroupId' --output text)
echo "   RDS Security Group: $RDS_SG_ID"

REDIS_SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$PROJECT_NAME-redis-sg" --query 'SecurityGroups[0].GroupId' --output text)
echo "   Redis Security Group: $REDIS_SG_ID"

#############################################
# 4. Create RDS PostgreSQL (Free Tier)
#############################################
echo ""
echo "🗄️ Step 4: Creating RDS PostgreSQL Database (Free Tier)..."

# Check if RDS already exists
RDS_EXISTS=$(aws rds describe-db-instances --db-instance-identifier "$PROJECT_NAME-db" 2>/dev/null || echo "not_found")

if [[ "$RDS_EXISTS" == "not_found" ]]; then
    aws rds create-db-instance \
        --db-instance-identifier "$PROJECT_NAME-db" \
        --db-instance-class db.t3.micro \
        --engine postgres \
        --engine-version "16.8" \
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
    echo "   ⏳ RDS instance is being created..."
else
    echo "   ℹ️ RDS already exists, skipping..."
fi

#############################################
# 5. Create ElastiCache Redis
#############################################
echo ""
echo "⚡ Step 5: Creating ElastiCache Redis..."

# Check if subnet group exists
REDIS_SUBNET_EXISTS=$(aws elasticache describe-cache-subnet-groups --cache-subnet-group-name "$PROJECT_NAME-redis-subnet-group" 2>/dev/null || echo "not_found")

if [[ "$REDIS_SUBNET_EXISTS" == "not_found" ]]; then
    aws elasticache create-cache-subnet-group \
        --cache-subnet-group-name "$PROJECT_NAME-redis-subnet-group" \
        --cache-subnet-group-description "Subnet group for HMS Redis" \
        --subnet-ids $SUBNET_PRIVATE_1 $SUBNET_PRIVATE_2
fi

# Check if Redis cluster exists
REDIS_EXISTS=$(aws elasticache describe-cache-clusters --cache-cluster-id "$PROJECT_NAME-redis" 2>/dev/null || echo "not_found")

if [[ "$REDIS_EXISTS" == "not_found" ]]; then
    aws elasticache create-cache-cluster \
        --cache-cluster-id "$PROJECT_NAME-redis" \
        --cache-node-type cache.t3.micro \
        --engine redis \
        --num-cache-nodes 1 \
        --cache-subnet-group-name "$PROJECT_NAME-redis-subnet-group" \
        --security-group-ids $REDIS_SG_ID \
        --tags Key=Name,Value="$PROJECT_NAME-redis"
    echo "   ⏳ Redis cluster is being created..."
else
    echo "   ℹ️ Redis already exists, skipping..."
fi

#############################################
# 6. Create IAM Role for EC2
#############################################
echo ""
echo "👤 Step 6: Creating IAM Role for EC2..."

# Check if role exists
ROLE_EXISTS=$(aws iam get-role --role-name "$PROJECT_NAME-ec2-role" 2>/dev/null || echo "not_found")

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
        --assume-role-policy-document file:///tmp/ec2-trust-policy.json

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

    aws iam attach-role-policy \
        --role-name "$PROJECT_NAME-ec2-role" \
        --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

    echo "   ✅ IAM Role created"
else
    echo "   ℹ️ IAM Role already exists"
fi

# Create Instance Profile
PROFILE_EXISTS=$(aws iam get-instance-profile --instance-profile-name "$PROJECT_NAME-ec2-profile" 2>/dev/null || echo "not_found")

if [[ "$PROFILE_EXISTS" == "not_found" ]]; then
    aws iam create-instance-profile --instance-profile-name "$PROJECT_NAME-ec2-profile"
    aws iam add-role-to-instance-profile \
        --instance-profile-name "$PROJECT_NAME-ec2-profile" \
        --role-name "$PROJECT_NAME-ec2-role"
    echo "   ✅ Instance Profile created"
    sleep 10
else
    echo "   ℹ️ Instance Profile already exists"
fi

#############################################
# 7. Create EC2 Key Pair
#############################################
echo ""
echo "🔑 Step 7: Creating EC2 Key Pair..."

KEY_EXISTS=$(aws ec2 describe-key-pairs --key-names $EC2_KEY_NAME 2>/dev/null || echo "not_found")

if [[ "$KEY_EXISTS" == "not_found" ]]; then
    aws ec2 create-key-pair \
        --key-name $EC2_KEY_NAME \
        --query 'KeyMaterial' \
        --output text > /tmp/$EC2_KEY_NAME.pem
    chmod 400 /tmp/$EC2_KEY_NAME.pem
    echo "   ✅ Key Pair created: /tmp/$EC2_KEY_NAME.pem"
else
    echo "   ℹ️ Key Pair already exists"
fi

#############################################
# 8. Create EC2 Instance (Free Tier: t3.micro)
#############################################
echo ""
echo "🖥️ Step 8: Creating EC2 Instance (t3.micro - Free Tier)..."

# Check if instance exists
INSTANCE_EXISTS=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$PROJECT_NAME-server" "Name=instance-state-name,Values=running,pending" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text 2>/dev/null)

if [[ "$INSTANCE_EXISTS" == "None" ]] || [[ -z "$INSTANCE_EXISTS" ]]; then
    # Get latest Ubuntu 22.04 AMI
    AMI_ID=$(aws ec2 describe-images \
        --owners 099720109477 \
        --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
        --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
        --output text)
    echo "   Using AMI: $AMI_ID"

    cat > /tmp/user-data.sh << 'USERDATA'
#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx git

systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

mkdir -p /opt/hms
chown ubuntu:ubuntu /opt/hms

echo "EC2 setup complete!" > /home/ubuntu/setup-complete.txt
USERDATA

    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $EC2_INSTANCE_TYPE \
        --key-name $EC2_KEY_NAME \
        --security-group-ids $EC2_SG_ID \
        --subnet-id $SUBNET_PUBLIC_1 \
        --iam-instance-profile Name="$PROJECT_NAME-ec2-profile" \
        --user-data file:///tmp/user-data.sh \
        --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20,"VolumeType":"gp2"}}]' \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$PROJECT_NAME-server}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
    echo "   ⏳ EC2 instance launching: $INSTANCE_ID"
    
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    echo "   ✅ EC2 Instance running: $INSTANCE_ID"
else
    INSTANCE_ID=$INSTANCE_EXISTS
    echo "   ℹ️ EC2 Instance already exists: $INSTANCE_ID"
fi

#############################################
# 9. Create/Get Elastic IP
#############################################
echo ""
echo "🌍 Step 9: Setting up Elastic IP..."

# Check for existing EIP
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
    echo "   ✅ Elastic IP allocated: $ALLOCATION_ID"
else
    ALLOCATION_ID=$EXISTING_EIP
    echo "   ℹ️ Using existing Elastic IP: $ALLOCATION_ID"
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
# 10. Create IAM User for Application
#############################################
echo ""
echo "👤 Step 10: Creating IAM User for Application..."

USER_EXISTS=$(aws iam get-user --user-name "$PROJECT_NAME-app-user" 2>/dev/null || echo "not_found")

if [[ "$USER_EXISTS" == "not_found" ]]; then
    aws iam create-user --user-name "$PROJECT_NAME-app-user"

    ACCESS_KEY_OUTPUT=$(aws iam create-access-key --user-name "$PROJECT_NAME-app-user")
    AWS_ACCESS_KEY_ID=$(echo $ACCESS_KEY_OUTPUT | python3 -c "import sys, json; print(json.load(sys.stdin)['AccessKey']['AccessKeyId'])")
    AWS_SECRET_ACCESS_KEY=$(echo $ACCESS_KEY_OUTPUT | python3 -c "import sys, json; print(json.load(sys.stdin)['AccessKey']['SecretAccessKey'])")

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

    echo "   ✅ IAM User created"
    echo "   🔑 Access Key ID: $AWS_ACCESS_KEY_ID"
else
    echo "   ℹ️ IAM User already exists"
    AWS_ACCESS_KEY_ID="(check existing keys)"
    AWS_SECRET_ACCESS_KEY="(check existing keys)"
fi

#############################################
# Wait for RDS
#############################################
echo ""
echo "⏳ Waiting for RDS to be available (5-10 minutes)..."
aws rds wait db-instance-available --db-instance-identifier "$PROJECT_NAME-db" 2>/dev/null || true

RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier "$PROJECT_NAME-db" \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text 2>/dev/null || echo "pending")

echo "   ✅ RDS Endpoint: $RDS_ENDPOINT"

#############################################
# Wait for Redis
#############################################
echo ""
echo "⏳ Waiting for Redis..."
aws elasticache wait cache-cluster-available --cache-cluster-id "$PROJECT_NAME-redis" 2>/dev/null || true

REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
    --cache-cluster-id "$PROJECT_NAME-redis" \
    --show-cache-node-info \
    --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
    --output text 2>/dev/null || echo "pending")

echo "   ✅ Redis Endpoint: $REDIS_ENDPOINT"

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
echo "    SSH: ssh -i hms-key-pair.pem ubuntu@$ELASTIC_IP"
echo ""
echo "🗄️  DATABASE (RDS PostgreSQL):"
echo "    Endpoint: $RDS_ENDPOINT"
echo "    Database: $DB_NAME"
echo "    Username: $DB_USER"
echo "    Password: $DB_PASSWORD"
echo ""
echo "⚡ REDIS (ElastiCache):"
echo "    Endpoint: $REDIS_ENDPOINT"
echo ""
echo "📦 S3 BUCKET:"
echo "    Bucket: $S3_BUCKET_NAME"
echo ""
echo "🔑 AWS CREDENTIALS (for app):"
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
echo "============================================"

# Save credentials
cat > /tmp/hms-credentials.txt << EOF
============================================
HMS AWS CREDENTIALS - $(date)
============================================

EC2:
  Instance ID: $INSTANCE_ID
  Elastic IP: $ELASTIC_IP
  SSH: ssh -i hms-key-pair.pem ubuntu@$ELASTIC_IP

DATABASE:
  Endpoint: $RDS_ENDPOINT
  Database: $DB_NAME
  Username: $DB_USER
  Password: $DB_PASSWORD

REDIS:
  Endpoint: $REDIS_ENDPOINT

S3:
  Bucket: $S3_BUCKET_NAME

AWS CREDENTIALS:
  Access Key ID: $AWS_ACCESS_KEY_ID
  Secret Access Key: $AWS_SECRET_ACCESS_KEY

SECRETS:
  Django Secret Key: $DJANGO_SECRET_KEY
  AES Encryption Key: $AES_ENCRYPTION_KEY

DNS: Point vakverse.com and www.vakverse.com to $ELASTIC_IP
EOF

echo "📁 Credentials saved to: /tmp/hms-credentials.txt"

# Copy key to Desktop
if [[ -f /tmp/$EC2_KEY_NAME.pem ]]; then
    cp /tmp/$EC2_KEY_NAME.pem ~/Desktop/$EC2_KEY_NAME.pem 2>/dev/null || true
    echo "🔑 SSH Key copied to: ~/Desktop/$EC2_KEY_NAME.pem"
fi
