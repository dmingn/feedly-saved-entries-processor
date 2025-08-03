# Language Policy

## Development Language

All code, documentation (including code comments), and commit messages MUST be written in English.

## Conversational Language

The language used for communication and conversation with the user should match the language the user is using.

# Commit Message Generation

When creating a commit message, the agent MUST adhere to the following rules:

1.  **Base on Git Diff Only:** The commit message MUST be based solely on the output of `git diff --staged` or `git diff HEAD`. The agent MUST ignore conversation history and work logs.
2.  **Follow Conventional Commits:** The commit message MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
