## Basic information about the meeting

- **DATE**: 2025/10/25
- **TIME**: 15:00 - 15:15
- **Moderator**: Wen Peixuan
- **Recorder**: Wen Peixuan
- **Participant**: Wen Peixuan,  Wang Jingchu, Li Muyu, Liang Dasi, Zhang Lin
- **Absentees**: Chen Ting

## Agenda of the meeting

- Review progress on Sprint 2 tasks
- Address issues arising from the recent project restructuring
- Coordinate next steps for development, testing, and documentation

## Discussion points and decision-making

### 1. Progress Updates

**Backend (Liang Dasi)**:
- Completed a significant **restructuring of the project directory** to improve organization, as requested by the frontend.
- Has largely completed the development of the **three core Sprint 2 features** (Member Contribution, Issue Response Time, Code Review Efficiency).
- Will create and push feature branches for these new functionalities after the structural Pull Request (PR) is merged.

**Backend (Wang Jingchu)**:
- Confirmed that both the original burndown chart and the new components are functional under the new project structure.
- Clarified that the main executable file has moved; users must now run the new Python file in the root directory.
- Collaborated with the frontend on developing a **new query interface feature** that accepts a project URL for analysis, with progress reported as smooth.

**Testing (Zhang Lin)**:
- No new features were ready for testing this week.
- Focused on adding an **automated testing workflow**.
- Awaiting the stabilization of the new project structure and the new feature branches to resume comprehensive testing.

**Documentation (Li Muyu)**:
- In the process of documenting work completed in Sprint 1 by the frontend and testing roles.
- Requested that the **backend developers provide a summary of their Sprint 1 functionalities** for inclusion in the project report, using the format shared by the frontend as a reference.

### 2. Key Discussions and Decisions

**Project Restructuring & Merge Process**:
- A PR for the project structure changes is pending.
- **Decision**: The PM (Wen Peixuan) is responsible for reviewing and merging this PR.
- **Action**: All developers (especially frontend and testing) need to update their local paths and code to align with the new directory structure once the PR is merged.

**Code Organization Standardization**:
- A discussion ensued about logically separating core calculation modules (to be placed in a `matrix`-like folder) from the main execution scripts and test files.
- **Decision**: Adopt a clearer folder structure:
    - Core computational classes/modules in a dedicated folder (e.g., `metrics`).
    - Main execution scripts in a core project folder.
    - Test code in a separate `tests` folder.
    - Documentation in its own folder.
- **Action**: Backend developers (Liang Dasi, Wang Jingchu) to finalize this organization in the codebase.

**Documentation Sync**:
- **Decision**: Backend developers will provide a summary of their Sprint 1 work to Li Muyu for documentation.

### 3. Action Items

- **Wen Peixuan (PM)**: Review and merge the project structure PR. Monitor the creation of new feature branches.
- **Liang Dasi & Wang Jingchu (Backend)**:
    1.  Finalize and push the three new feature branches after the structure PR is merged.
    2.  Provide a summary of Sprint 1 backend features to Li Muyu.
    3.  Collaborate to implement the agreed-upon folder structure for core modules.
- **Chen Ting (Frontend)**: Continue collaboration on the query interface and adapt to the new project structure.
- **Zhang Lin (Testing)**: Update automated tests to work with the new structure and prepare to test the new feature branches once available.
- **Li Muyu (Documentation)**: Integrate backend Sprint 1 summaries and continue updating the project report.
