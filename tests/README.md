# ES cluster creation

This script will provision:
- a simple AWS ES node
- deploy the `es-cleanup` module
- create multiple index


## How to

Just run

```
./run.sh

```

## Notes

This demo script will save the terraform state in you local folder.

Remember to destroy your test scenario using the command:

```
terraform destroy -auto-approve
```
