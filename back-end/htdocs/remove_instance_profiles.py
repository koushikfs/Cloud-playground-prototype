import boto3

# Create IAM client
iam = boto3.client('iam')

# List all instance profiles
instance_profiles = iam.list_instance_profiles()['InstanceProfiles']

# Loop through each profile and delete it
for profile in instance_profiles:
    profile_name = profile['InstanceProfileName']

    # Detach roles associated with the instance profile
    roles = profile['Roles']
    for role in roles:
        role_name = role['RoleName']
        iam.remove_role_from_instance_profile(InstanceProfileName=profile_name, RoleName=role_name)

    # Delete the instance profile
    iam.delete_instance_profile(InstanceProfileName=profile_name)
    print(f"Deleted instance profile: {profile_name}")

print("All instance profiles have been deleted.")
