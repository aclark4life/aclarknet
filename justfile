EB_ENV_NAME := "aclarknet"
EC2_INSTANCE_MIN := "1"
EC2_INSTANCE_MAX := "1"
EC2_INSTANCE_PROFILE := "eb-ec2-role"
EC2_INSTANCE_TYPE := "t2.micro"
EB_SSH_KEY := "aclarknet"
EB_PLATFORM := "Docker 17.09.0-ce"
EC2_LB_TYPE := "application"
VPC_ID := "vpc-0a1b2c3d4e5f6g7h8"
VPC_SUBNET_EC2 := "subnet-0a1b2c3d4e5f6g7h8"
VPC_SUBNET_ELB := "subnet-0a1b2c3d4e5f6g7h8"
VPC_SG := "sg-0461a71e4ee9c9d48"

default:
    echo 'Hello, world!'

pip-install:
    pip install -e .
alias i := pip-install

open:
    open http://localhost:8000
alias o := open

[group("aclarknet")]
fix-lounge:
	eb ssh -c "sudo rm -rvf /var/app/current/lounge/node_modules"
	eb ssh -c "cd /var/app/current/lounge; sudo npm install"
	eb ssh -c "sudo cp /tmp/aclark.json /var/app/current/lounge/.thelounge/users/aclark.json"
	eb ssh -c "sudo systemctl restart lounge"

[group("eb")]
eb-create:
    eb create {{EB_ENV_NAME}} \
         -im {{EC2_INSTANCE_MIN}} \
         -ix {{EC2_INSTANCE_MAX}} \
         -ip {{EC2_INSTANCE_PROFILE}} \
         -i {{EC2_INSTANCE_TYPE}} \
         -k {{EB_SSH_KEY}} \
         -p {{EB_PLATFORM}} \
         --elb-type {{EC2_LB_TYPE}} \
         --vpc \
         --vpc.id {{VPC_ID}} \
         --vpc.elbpublic \
         --vpc.publicip \
         --vpc.ec2subnets {{VPC_SUBNET_EC2}} \
         --vpc.elbsubnets {{VPC_SUBNET_ELB}} \
         --vpc.securitygroups {{VPC_SG}}

[group("ec2")]
sgs:
    aws ec2 describe-security-groups --output table
vpc:
    aws ec2 describe-vpcs --output table
