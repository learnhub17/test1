# Instance settings
image_id="ami-10acfb73" # ubuntu 16.04
ssh_key_name="new"
security_group="proxy"
instance_type="t2.micro"
region="ap-southeast-1"
root_vol_size=8
count=1

# Tags
tags_Name="proxyserver"
tags_Owner="test"
tags_ApplicationRole="Testing"
tags_Cluster="Test Cluster"
tags_Environment="dev"
tags_OwnerEmail="test@xxxx.com"
tags_Project="Test"
tags_BusinessUnit="Cloud Platform Engineering"
tags_SupportEmail="test@xxxx.com"

#check credentials
dir="/root/.aws"
#################
if [ -d "$dir" ];
 then
  echo "credential present"
 else
apt-get install -y python-pip 
pip install --upgrade pip
pip install awscli
pip install boto
echo "enter AccountID"
read accountID
echo "enter AccountKey"
read accountkey
aws configure set aws_access_key_id $accountID
aws configure set aws_secret_access_key $accountkey
aws configure set default.region ap-southeast-1
aws configure set default.output json
fi

# key creation
echo "checking keypair..."

if [ -f "${ssh_key_name}.pem" ];
  then
    echo "key exists..."
else
    echo "creating keypair..."
aws ec2 create-key-pair --key-name $ssh_key_name --query 'KeyMaterial' --output text > $PWD/${ssh_key_name}.pem
chmod 400 ${ssh_key_name}.pem
fi

# security group 
echo "creating security_group..."

aws ec2 create-security-group --group-name $security_group --description "Inbound SSH and Proxy allow"
aws ec2 authorize-security-group-ingress --group-name $security_group --cidr 0.0.0.0/0 --protocol tcp --port 22 
aws ec2 authorize-security-group-ingress --group-name $security_group --cidr 0.0.0.0/0 --protocol tcp --port 8118
aws ec2 authorize-security-group-ingress --group-name $security_group --cidr 0.0.0.0/0 --protocol tcp --port 9050 

#echo 'creating keypair'
#aws ec2 create-key-pair --key-name $ssh_key_name --query 'KeyMaterial' --output text > $PWD/${ssh_key_name}.pem
#chmod 400 ${ssh_key_name}.pem

# create instance
echo "creating instance..."

id=$(aws ec2 run-instances --region $region  --image-id $image_id --count $count --instance-type $instance_type --key-name $ssh_key_name --security-groups $security_group --block-device-mapping "[ { \"DeviceName\": \"/dev/sda1\", \"Ebs\": { \"VolumeSize\": $root_vol_size } } ]" --query 'Instances[*].InstanceId' --user-data file://package_proxy.sh --output text)

echo "$id created"
echo "$id" > id.txt
# tag it
echo "tagging $id..."

aws ec2 create-tags --resources $id --tags Key=Name,Value="$tags_Name" --region $region Key=Owner,Value="$tags_Owner"  Key=ApplicationRole,Value="$tags_ApplicationRole" Key=Cluster,Value="$tags_Cluster" Key=Environment,Value="$tags_Environment" Key=OwnerEmail,Value="$tags_OwnerEmail" Key=Project,Value="$tags_Project" Key=BusinessUnit,Value="$tags_BusinessUnit" Key=SupportEmail,Value="$tags_SupportEmail" Key=OwnerGroups,Value="$tags_OwnerGroups"

# store the data
echo "storing instance details..."

aws ec2 describe-instances --region $region  --instance-ids $id > proxy-instance.json

a="$(./ec2.py --refresh --list | grep -A2 tag_Name_$tags_Name | grep -oe '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}')" 
b=$a
echo $b | tr " " "\n" > proxy.txt
##
#sh crawlerinst.sh
