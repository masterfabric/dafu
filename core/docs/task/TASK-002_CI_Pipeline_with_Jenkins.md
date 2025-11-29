# [TASK-002] Establish a CI Pipeline with Jenkins

**Status:** `Open`  
**Priority:** `High`  
**Owner:** `Project Owner`  
**Assignee:** `Data Engineer`  

---

## 1. Project Owner's Perspective

### Goal
To automate our quality assurance process, ensuring that every code change is automatically tested before it is integrated. This will increase development velocity, improve code stability, and reduce the risk of introducing bugs into our production environment.

### User Story
"As a Development Team Lead, I want a Continuous Integration (CI) pipeline that automatically builds and tests every pull request and merge to the main branch, so that we can maintain a high standard of code quality and ensure the application is always in a deployable state."

### Value Proposition
- **Improved Code Quality:** Automatically enforces linting, style checks, and testing on all code changes.
- **Increased Stability:** Catches bugs and regressions early, before they reach the main codebase.
- **Faster Development Cycles:** Developers receive immediate feedback on their changes without manual intervention.
- **Reduced Risk:** Ensures that the main branch is always stable and ready for deployment.

### Acceptance Criteria
- A `Jenkinsfile` must be present in the root of the repository.
- The Jenkins pipeline must be triggered on every pull request and push to the `main` branch.
- The pipeline must successfully execute all stages: checkout, environment setup, dependency installation, linting, and testing.
- If any stage fails, the pipeline must fail and report the error.
- The pipeline status (success/failure) must be visible on the corresponding pull request in GitHub.

---

## 2. Technical Analysis & Implementation Plan

### Current State
The project currently relies on `.pre-commit-config.yaml` for local, manual quality checks. There is no automated CI server integration. The `README.md` contains a placeholder for a GitHub Actions workflow, but per our discussion, we are opting for Jenkins to align with enterprise standards.

### Proposed Solution
We will create a `Jenkinsfile` that defines a declarative pipeline. This file will serve as the "pipeline as code," allowing us to version control our CI process. The pipeline will use a standard Python environment to run all necessary quality and testing steps.

### Step-by-Step Implementation
1.  **Create `Jenkinsfile`:** In the root directory of the project, create a new file named `Jenkinsfile`.
2.  **Define Pipeline Agent:** Specify a Docker agent to ensure a clean and consistent build environment. We will use a standard Python image.
    ```groovy
    pipeline {
        agent {
            docker { image 'python:3.9-slim' }
        }
        // ... stages
    }
    ```
3.  **Define Pipeline Stages:** Create a series of sequential stages:
    - **`Checkout`:** Use the `checkout scm` step to pull the source code from the Git repository.
    - **`Setup Environment`:** This stage can be used to print Python/pip versions to the console for debugging.
    - **`Install Dependencies`:** Execute a shell command to install all project dependencies: `pip install -r requirements.txt`.
    - **`Lint & Quality Check`:** Execute the pre-commit hooks to run static analysis, linting, and formatting checks: `pip install pre-commit && pre-commit run --all-files`.
    - **`Run Unit Tests`:** Execute the test suite using `pytest`: `pip install pytest && pytest`.
4.  **Add Post-build Actions (Optional but Recommended):** Configure `post` conditions to clean up the workspace regardless of the build's success or failure.
5.  **Local Testing:** To test the `Jenkinsfile` without a full Jenkins server, you can use the [Jenkins Pipeline Linter](https://www.jenkins.io/doc/book/pipeline/development/#linter). You can also set up a local Jenkins instance using their official Docker image (`jenkins/jenkins:lts-jdk11`) to run the full pipeline.

### Key Files & Directories to Modify
- `/Jenkinsfile` (New file)

### Testing Strategy
- **Linting:** The `Jenkinsfile` itself can be linted using online tools or a local Jenkins instance.
- **Integration Test:** The primary test is to configure a Jenkins server to use this `Jenkinsfile`.
    1.  Set up a Jenkins server (e.g., via Docker).
    2.  Create a new "Pipeline" job.
    3.  Configure the job to use "Pipeline script from SCM."
    4.  Point it to this Git repository and specify `Jenkinsfile` as the script path.
    5.  Trigger a build and verify that all stages execute successfully.
- **Failure Test:** Intentionally introduce a syntax error or a failing test into a new branch and create a pull request. Verify that the Jenkins pipeline runs, fails at the appropriate stage, and reports the failure on the PR.

---
## 2.1. Deep Dive: Engineering Perspective

### Pipeline Strategy: Multi-branch vs. Standard
For a project with active feature development, a **Multi-branch Pipeline** is superior to a standard Pipeline job. When configured, Jenkins will automatically discover branches and pull requests in your repository, creating and managing jobs for them dynamically. This eliminates the manual step of creating a new Jenkins job for each new feature branch. This should be our target configuration.

### Code Reusability: Jenkins Shared Libraries
As our CI/CD process grows more complex (e.g., adding stages for building Docker images, deploying to staging), the `Jenkinsfile` can become bloated. To keep our pipeline code DRY (Don't Repeat Yourself), we should plan to use **Jenkins Shared Libraries**. We could create a separate repository for our shared library, which would contain reusable Groovy scripts for common tasks (e.g., `runPythonTests()`, `buildAndPushDockerImage()`). Our `Jenkinsfile` would then become much simpler, importing and calling these functions.

### Secure Credential Management
The pipeline may eventually need to interact with secure systems (e.g., pushing a Docker image to a private registry, deploying to a cloud environment). **Secrets must never be hardcoded in the `Jenkinsfile`**. The correct approach is to use the **Jenkins Credentials Manager**. We would store secrets (like passwords, API tokens, or SSH keys) in Jenkins, which assigns them a unique ID. The `Jenkinsfile` can then securely access these secrets by their ID.

Example:
```groovy
environment {
    DOCKER_HUB_CREDS = credentials('my-dockerhub-credentials-id')
}
stages {
    stage('Push Docker Image') {
        steps {
            sh 'docker login -u $DOCKER_HUB_CREDS_USR -p $DOCKER_HUB_CREDS_PSW'
            // ...
        }
    }
}
```

### Artifacts and Reporting
A CI pipeline should do more than just pass or fail. It should generate valuable reports.
- **Test Reports:** The `pytest` command should be modified to generate a JUnit XML report (`pytest --junitxml=test-results.xml`). We can then use the `junit` post-build step in our `Jenkinsfile` to parse these results, allowing Jenkins to track test history, display trends, and provide detailed failure analysis in the UI.
- **Code Coverage:** We can use a tool like `pytest-cov` to generate a code coverage report (`pytest --cov --cov-report=xml`). The Jenkins Cobertura Plugin can then parse this report to visualize coverage metrics and track them over time. This helps us ensure that new code is being adequately tested.
