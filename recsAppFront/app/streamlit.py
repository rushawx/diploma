import streamlit as st
from app.config import Settings
from handlers.auth_helpers import (
    get_user_profile,
    is_authenticated,
    is_token_expired,
    login,
    logout,
    make_authenticated_request,
    signup,
)
from handlers.transformers import (
    compile_tags_vector,
    get_model,
    get_tags_set,
    tags_search,
    transformer_search,
)

settings = Settings()

st.set_page_config(
    page_title=settings.APP_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
)

st.title(settings.APP_TITLE)


def display_project(project: dict, show_details: bool = False):
    """Display a project in a formatted way"""
    st.markdown(f"### {project.get('title_rus', 'Untitled')}")
    if project.get('title_eng'):
        st.caption(f"🇬🇧 {project.get('title_eng')}")
    if project.get('annotation'):
        st.info(f"📝 **Annotation:** {project.get('annotation')}")
    if project.get('description'):
        st.text(project.get('description', ''))
    if show_details:
        if project.get('created_at'):
            st.caption(f"📅 **Created:** {project.get('created_at')}")
        if project.get('modified_by'):
            st.caption(f"👤 **Modified by:** {project.get('modified_by')}")

if "model" not in st.session_state:
    st.session_state["model"] = get_model()
    st.success("Model loaded successfully!")

menu = [
    "Welcome Page",
    "Select Your Project",
    "Find Similar Projects by Tags",
    "View Available Projects",
    "View Project Details",
    "View My Projects",
    "Create Project",
    "Signup",
    "Login",
    "Profile",
]

choice = st.sidebar.selectbox("Choose an option", menu)

if choice == "Welcome Page":
    st.subheader("Welcome Page")
    st.text("This is the welcome page of Student Projects Recommender System")
elif choice == "Select Your Project":
    st.subheader("Select Your Project")
    if is_authenticated():
        if is_token_expired():
            st.warning("Session expired. Please login again.")
        else:
            model = get_model()
            query = st.text_input("Enter approximate project topic")
            if query:
                results = transformer_search(model, query)
                if not results.empty:
                    st.markdown("### Similar Projects Found")

                    project_options = {f"{row.get('title_rus', 'Untitled')} ({row.get('score', 0):.2f})": row.get('project', {}).get('id') for _, row in results.iterrows()}

                    selected_project_name = st.selectbox("Select a project to claim as yours", list(project_options.keys()))

                    if st.button("Claim Selected Project"):
                        if selected_project_name:
                            project_id = project_options[selected_project_name]
                            try:
                                response = make_authenticated_request("PUT", f"/projects/{project_id}", json={})
                                if response.status_code == 200:
                                    st.success("✅ Project claimed successfully!")
                                    updated_project = response.json()
                                    st.markdown("### Your New Project:")
                                    display_project(updated_project, show_details=True)
                                    if st.button("Search for Another Project"):
                                        st.rerun()
                                elif response.status_code == 404:
                                    st.error("Project not found")
                                else:
                                    st.error(f"Failed to claim project: {response.status_code}")
                            except Exception as e:
                                st.error(f"Error claiming project: {str(e)}")

                    st.markdown("---")
                    st.markdown("#### Available Similar Projects:")
                    for _, row in results.iterrows():
                        project = row.get('project', {})
                        st.markdown(f"**{row.get('title_rus', 'Untitled')}** (Similarity: {row.get('score', 0):.2f})")
                        if project.get('title_eng'):
                            st.caption(f"🇬🇧 {project.get('title_eng')}")
                        if project.get('annotation'):
                            st.info(project.get('annotation'))
                        st.text(project.get('description', ''))
                        st.markdown("---")
                else:
                    st.info("No similar projects found")
    else:
        st.warning("Please login to access this feature")
elif choice == "Find Similar Projects by Tags":
    st.subheader("Find Similar Projects by Tags")
    if is_authenticated():
        if is_token_expired():
            st.warning("Session expired. Please login again.")
        else:
            st.markdown("Select multiple tags to find projects with similar tags using cosine similarity.")

            # Load available tags
            available_tags = get_tags_set()

            if not available_tags:
                st.error("No tags available. Please ensure tags_set.pkl file exists.")
            else:
                st.info(f"📋 Available tags: {len(available_tags)}")

                # Multi-select for tags
                selected_tags = st.multiselect(
                    "Select tags (choose one or more)",
                    options=available_tags,
                    help="Choose multiple tags to find projects with similar tag combinations"
                )

                if selected_tags:
                    st.write(f"✅ Selected tags: {', '.join(selected_tags)}")

                    # Search button
                    if st.button("Find Projects with Similar Tags"):
                        if not selected_tags:
                            st.error("Please select at least one tag")
                        else:
                            with st.spinner("Searching for projects with similar tags..."):
                                # Compile tags vector from selected tags
                                tags_vector = compile_tags_vector(selected_tags)

                                # Search for similar projects
                                results = tags_search(tags_vector=tags_vector)

                                if not results.empty:
                                    st.success(f"Found {len(results)} projects with similar tags!")

                                    # Show results
                                    for _, row in results.iterrows():
                                        project = row.get('project', {})
                                        similarity_score = row.get('score', 0)

                                        st.markdown(f"### {project.get('title_rus', 'Untitled')}")
                                        st.caption(f"🏷️ Tags Similarity: {similarity_score:.2f}")

                                        if project.get('title_eng'):
                                            st.caption(f"🇬🇧 {project.get('title_eng')}")

                                        if project.get('annotation'):
                                            st.info(f"📝 **Annotation:** {project.get('annotation')}")

                                        if project.get('description'):
                                            st.text(project.get('description', ''))

                                        st.markdown("---")
                                else:
                                    st.info("No projects found with similar tags")
                else:
                    st.info("👆 Select tags above to search for similar projects")
    else:
        st.warning("Please login to access this feature")
elif choice == "View Available Projects":
    st.subheader("View Available Projects")
    if is_authenticated():
        try:
            response = make_authenticated_request("GET", "/projects/")
            if response.status_code == 200:
                projects = response.json()
                if projects:
                    st.success(f"Found {len(projects)} available projects")
                    for project in projects:
                        display_project(project)
                        st.markdown("---")
                else:
                    st.info("No projects available")
            else:
                st.error(f"Failed to fetch projects: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please login to access this feature")
elif choice == "View Project Details":
    st.subheader("View Project Details")
    if is_authenticated():
        try:
            projects_response = make_authenticated_request("GET", "/projects/")
            if projects_response.status_code == 200:
                all_projects = projects_response.json()
                if all_projects:
                    project_options = {p.get('title_rus', 'Untitled'): p.get('id') for p in all_projects}
                    selected_project = st.selectbox("Select a project to view details", list(project_options.keys()))

                    if selected_project:
                        project_id = project_options[selected_project]
                        try:
                            response = make_authenticated_request("GET", f"/projects/{project_id}")
                            if response.status_code == 200:
                                project = response.json()
                                st.markdown(f"## 📋 Project Details")
                                display_project(project, show_details=True)
                            elif response.status_code == 404:
                                st.error("Project not found")
                            else:
                                st.error(f"Failed to fetch project: {response.status_code}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("No projects available to select")
            else:
                st.error(f"Failed to fetch projects list: {projects_response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please login to access this feature")
elif choice == "View My Projects":
    st.subheader("View My Projects")
    if is_authenticated():
        try:
            profile = get_user_profile()
            if profile:
                user_id = profile.get('id')
                if user_id:
                    response = make_authenticated_request("GET", f"/projects/user/{user_id}")
                    if response.status_code == 200:
                        projects = response.json()
                        if projects:
                            st.success(f"Found {len(projects)} projects for you")
                            for project in projects:
                                display_project(project)
                                st.markdown("---")
                        else:
                            st.info("No projects found for your account")
                    else:
                        st.error(f"Failed to fetch projects: {response.status_code}")
                else:
                    st.error("Could not retrieve user ID from profile")
            else:
                st.error("Could not retrieve user profile")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please login to access this feature")
elif choice == "Create Project":
    st.subheader("Create New Project")
    if is_authenticated():
        st.markdown("Fill in the project details below:")

        title_rus = st.text_input("Project Title (Russian)*", placeholder="Введите название проекта на русском")
        title_eng = st.text_input("Project Title (English)", placeholder="Enter project title in English")
        annotation = st.text_area("Annotation", placeholder="Short description or summary")
        description = st.text_area("Full Description", placeholder="Detailed description of the project")

        if st.button("Create Project"):
            if not title_rus:
                st.error("Project title (Russian) is required")
            else:
                with st.spinner("Generating embedding for your project..."):
                    model = get_model()

                    text_data = title_rus
                    if annotation:
                        text_data += " " + annotation
                    if description:
                        text_data += " " + description

                    text_data = text_data.replace("\n", " ").replace("\r", " ").replace("\t", " ")

                    embedding = model.encode([text_data])[0].tolist()

                project_data = {
                    "title_rus": title_rus,
                    "embedding": embedding,
                }
                if title_eng:
                    project_data["title_eng"] = title_eng
                if annotation:
                    project_data["annotation"] = annotation
                if description:
                    project_data["description"] = description

                try:
                    response = make_authenticated_request(
                        "POST",
                        "/projects/",
                        json=project_data
                    )

                    if response.status_code == 201:
                        st.success("Project created successfully! 🎉")
                        created_project = response.json()
                        st.markdown("### Your new project:")
                        display_project(created_project, show_details=True)
                        if st.button("Create Another Project"):
                            st.rerun()
                    else:
                        st.error(f"Failed to create project: {response.status_code}")
                        if response.text:
                            st.error(response.json().get('detail', 'Unknown error'))
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.warning("Please login to access this feature")
elif choice == "Signup":
    st.subheader("Signup")
    nick_name = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Signup"):
        if nick_name and password:
            signup(nick_name, password)
        else:
            st.error("Please enter both username and password")
elif choice == "Login":
    st.subheader("Login")
    nick_name = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if nick_name and password:
            if login(nick_name, password):
                st.success("Login successful!")
                st.rerun()
        else:
            st.error("Please enter both username and password")
elif choice == "Profile":
    st.subheader("Profile")
    if is_authenticated():
        profile = get_user_profile()
        if profile:
            st.json(profile)
    else:
        st.warning("Please login to view your profile")

if is_authenticated() and st.sidebar.button("Logout"):
    logout()
    st.rerun()

if is_authenticated():
    st.sidebar.success(f"Logged in as: {st.session_state.get('username', 'Unknown')}")
