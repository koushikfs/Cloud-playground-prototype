import json
import sys

def generate_terraform_script(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    terraform_script_parts = [
    f'provider "aws" {{\n',
    f'  region = "ap-south-1"\n',
    f'  access_key = "[]"\n',
    f'  secret_key = "[]"\n',
    f'}}\n\n']

    ec2_s3_access_map = {}
    elb_ec2_map = {}

    s3_buckets = []
    for node in data['nodes']:
      resource_id = node['id']
      resource_type = node['data']['label']

      if resource_type == 's3':
          s3_buckets.append(f'my-s3-bucket-{resource_id}')

    # Fetch the default VPC
    terraform_script_parts.append('variable "subnet_ids"{\n'
                                  '  description = "Subnet IDs for EC2 and ELB"\n'
                                  '  type        = list(string)\n'
                                  '  default     = ["subnet-054bf2b603fc5f3fd", "subnet-0da6e05a68baec7f4"]\n}\n\n')
    
    terraform_script_parts.append('variable "vpc_id"{\n'
                                  '  description = "VPC ID for EC2 and ELB"\n'
                                  '  type        = string\n'
                                  '  default     = "vpc-01871cb58ed97f8f5"\n}\n\n')
    
    terraform_script_parts.append('''
resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow SSH inbound traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}\n
''')
    
    terraform_script_parts.append('''
resource "aws_security_group" "allow_outbound" {
  name        = "allow_outbound"
  description = "Allow ALL outbound traffic"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
''')
    
    terraform_script_parts.append('''
resource "aws_security_group" "allow_http" {
  name        = "allow_http"
  description = "Allow port 80 from anywhere"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow traffic from anywhere
  }
}\n
''')

    for edge in data['edges']:
        source_node = edge['source']
        target_node = edge['target']

        if source_node.startswith('ec2') and target_node.startswith('s3'):
            ec2_s3_access_map[source_node] = target_node

        if source_node.startswith('ec2') and target_node.startswith('elb'):
            elb_ec2_map.setdefault(target_node, []).append(source_node)

    terraform_script_parts.append(
        f'resource "aws_lb_target_group" "common_target_group" {{\n'
        f'  name        = "my-common-target-group"\n'
        '  port        = 80\n'
        '  protocol    = "HTTP"\n'
        '  target_type = "instance"\n'
        '  vpc_id      = var.vpc_id\n'
        '}\n\n'
    )
    for elb_instance, ec2_instances in elb_ec2_map.items():
        for ec2_instance in ec2_instances:
            terraform_script_parts.append(
                f'resource "aws_lb_target_group_attachment" "target_attachment_{ec2_instance}_{elb_instance}" {{\n'
                f'  target_group_arn = aws_lb_target_group.common_target_group.arn\n'
                f'  target_id        = aws_instance.{ec2_instance}.id\n'
                '}\n\n'
            )

    terraform_script_parts.append(
        f'resource "aws_iam_role" "iam_role_common" {{\n'
        f'  name = "EC2S3AccessRole-common"\n'
        '  assume_role_policy = jsonencode({\n'
        '    Version = "2012-10-17",\n'
        '    Statement = [{\n'
        '      Action = "sts:AssumeRole",\n'
        '      Effect = "Allow",\n'
        '      Principal = { Service = "ec2.amazonaws.com" }\n'
        '    }]\n'
        '  })\n}\n\n'
    )

    policy_statements = []
    for s3_bucket in s3_buckets:
        policy_statements.append({
            'Action': ["s3:GetObject", "s3:PutObject","s3:ListBucket","s3:DeleteObject","iam:GenerateCredentialReport",
                "iam:GenerateServiceLastAccessedDetails",
                "iam:Get*",
                "iam:List*",
                "iam:SimulateCustomPolicy",
                "iam:SimulatePrincipalPolicy"],
            'Effect': "Allow",
            'Resource': [f"arn:aws:s3:::{s3_bucket}/*","*"]
        })

    terraform_script_parts.append(
        f'resource "aws_iam_role_policy" "iam_policy_common" {{\n'
        f'  name = "EC2S3AccessPolicy-common"\n'
        '  role = aws_iam_role.iam_role_common.id\n'
        '  policy = jsonencode({\n'
        '    Version = "2012-10-17",\n'
        '    Statement = ' + json.dumps(policy_statements) + '\n'
        '  })\n}\n\n'
    )

    terraform_script_parts.append(
        f'resource "aws_iam_instance_profile" "ec2_profile_s3" {{\n'
        f'  name = "EC2-S3-InstanceProfile"\n'
        f'  role = aws_iam_role.iam_role_common.name\n'
        '}\n\n'
    )

    for node in data['nodes']:
        resource_id = node['id']
        resource_type = node['data']['label']

        if resource_type == 'ec2':
            terraform_script_parts.append(
                f'resource "aws_instance" "{resource_id}" {{\n'
                '  tags = {\n'
                f'    Name = "Ec2-instance-{resource_id}"\n'
                '  }\n'
                '  ami                    = "ami-0a0f1259dd1c90938"\n'
                '  vpc_security_group_ids = [aws_security_group.allow_ssh.id,aws_security_group.allow_outbound.id,aws_security_group.allow_http.id]\n'
                '  instance_type          = "t2.micro"\n'
                '  root_block_device {\n'
                '    volume_type = "gp3"\n'
                '    volume_size = 8\n'
                '  }\n'
                f'  subnet_id              = var.subnet_ids[0]\n'
                '  user_data     = file("./web-server.sh")\n')
            if ec2_s3_access_map.get(resource_id, "").startswith("s3"):
                terraform_script_parts.append(
                    '  iam_instance_profile = aws_iam_instance_profile.ec2_profile_s3.name\n' 
                    '}\n\n')
            else:
                terraform_script_parts.append('}\n\n')

        elif resource_type == 's3':
          terraform_script_parts.append(f'resource "aws_s3_bucket" "{resource_id}" {{\n' 
                                        f'  bucket = "my-s3-bucket-{resource_id}"\n'
                                        '}\n\n')
          s3_buckets.append(f'my-s3-bucket-{resource_id}')


        elif resource_type == 'elb':
            terraform_script_parts.append(f'resource "aws_lb" "{resource_id}" {{\n'
                                          f'  name               = "my-elb-{resource_id}"\n'
                                          '  internal           = false\n'
                                          '  load_balancer_type = "application"\n'
                                          '  security_groups    = [aws_security_group.allow_http.id,aws_security_group.allow_outbound.id]\n'
                                          '  enable_deletion_protection = false\n'
                                          '  subnets         = var.subnet_ids\n'
                                          '}\n\n')
            terraform_script_parts.append(f'resource "aws_lb_listener" "listener-{resource_id}" {{\n'
                                          f'  load_balancer_arn = aws_lb.{resource_id}.arn\n'
                                          '  port              = 80\n'
                                          '  protocol          = "HTTP"\n\n'

                                          '  default_action {\n'
                                          '    type = "forward"\n'
                                          '    target_group_arn = aws_lb_target_group.common_target_group.arn\n'
                                          '    fixed_response {\n'
                                          '      content_type = "text/plain"\n'
                                          '      status_code  = "200"\n'
                                          '    }\n'
                                          '  }\n'
                                          '}'
                                      )

    return ''.join(terraform_script_parts)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test.py input.json")
        sys.exit(1)

    json_file_path = sys.argv[1]
    generated_script = generate_terraform_script(json_file_path)
    print(generated_script)

if __name__ == "__main__":
    main()
