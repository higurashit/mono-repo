# migration_tool

- [設計書](./design.md)

# commands (in cloudshell)
- `git clone https://github.com/higurashit/mono-repo.git`
- `cd mono-repo/services/migration_tool/iac/`
- `sam validate`
- `sam build`
- `sam package`
- `sam deploy --no-execute-changeset`
- `sam deploy`