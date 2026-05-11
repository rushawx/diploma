import streamlit as st
from app.config import Settings
from handlers.auth_helpers import (
    add_user_tags,
    auto_assign_avatar,
    get_all_avatars,
    get_avatar_recommendations,
    get_my_avatar,
    get_user_profile,
    is_authenticated,
    is_token_expired,
    login,
    logout,
    make_authenticated_request,
    select_avatar,
    signup,
)
from handlers.transformers import (
    compile_tags_vector,
    get_lightfm_model,
    get_lightfm_recommendations,
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
    if project.get("title_eng"):
        st.caption(f"🇬🇧 {project.get('title_eng')}")
    if project.get("annotation"):
        st.info(f"📝 **Annotation:** {project.get('annotation')}")
    if project.get("description"):
        st.text(project.get("description", ""))
    if show_details:
        if project.get("created_at"):
            st.caption(f"📅 **Created:** {project.get('created_at')}")
        if project.get("modified_by"):
            st.caption(f"👤 **Modified by:** {project.get('modified_by')}")


def claim_project(project_id: int) -> bool:
    """Claim a project for the current user"""
    try:
        profile = get_user_profile()
        if not profile:
            st.error("Could not retrieve user profile")
            return False

        user_id = profile.get("id")
        response = make_authenticated_request(
            "PUT", f"/projects/{project_id}", json={"chosen_by": user_id}
        )

        if response.status_code == 200:
            st.success("✅ Project claimed successfully!")
            updated_project = response.json()
            st.markdown("### Your New Project:")
            display_project(updated_project, show_details=True)
            return True
        elif response.status_code == 404:
            st.error("Project not found")
            return False
        else:
            st.error(f"Failed to claim project: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error claiming project: {str(e)}")
        return False


def rate_project(project_id: str, rating: int) -> bool:
    """Rate a project (1-5 stars)"""
    try:
        profile = get_user_profile()
        if not profile:
            st.error("Could not retrieve user profile")
            return False

        user_id = profile.get("id")
        response = make_authenticated_request(
            "POST", "/projects/rate", json={"project_id": project_id, "rating": rating}
        )

        if response.status_code == 201:
            st.success(f"✅ Rated project {rating} stars!")
            return True
        else:
            st.error(f"Failed to rate project: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error rating project: {str(e)}")
        return False


def get_project_rating(project_id: str) -> int:
    """Get current user's rating for a project"""
    try:
        profile = get_user_profile()
        if not profile:
            return 0

        response = make_authenticated_request("GET", f"/projects/{project_id}/rating")
        if response.status_code == 200:
            rating = response.json()
            return rating.get("rating", 0)
        return 0
    except Exception as e:
        return 0


def get_rated_project_ids(user_id: str) -> set:
    """Get set of project IDs already rated by user"""
    try:
        response = make_authenticated_request("GET", "/projects/ratings/all")
        if response.status_code == 200:
            all_ratings = response.json()
            return {
                rating["project_id"]
                for rating in all_ratings
                if rating["user_id"] == user_id
            }
        return set()
    except Exception as e:
        return set()


def filter_by_rated_projects(results_df, rated_project_ids: set):
    """Filter results DataFrame to exclude already rated projects"""
    if results_df.empty:
        return results_df
    return results_df[
        ~results_df["project"].apply(lambda p: p.get("id") in rated_project_ids)
    ]


def create_project_selectbox_options(filtered_results_df):
    """Create a dict of project options for selectbox from filtered results"""
    if filtered_results_df.empty:
        return {}
    return {
        f"{row.get('title_rus', 'Untitled')} ({row.get('score', 0):.2f})": row.get(
            "project", {}
        ).get("id")
        for _, row in filtered_results_df.iterrows()
    }


def display_search_result(project: dict, score: float, score_label: str = "Similarity"):
    """Display a search result project with score"""
    st.markdown(f"### {project.get('title_rus', 'Untitled')}")
    st.caption(f"🏷️ {score_label}: {score:.2f}")

    if project.get("title_eng"):
        st.caption(f"🇬🇧 {project.get('title_eng')}")

    if project.get("annotation"):
        st.info(f"📝 **Annotation:** {project.get('annotation')}")

    if project.get("description"):
        st.text(project.get("description", ""))

    st.markdown("---")


def display_avatar_info(avatar: dict):
    """Display avatar information in a 2-column layout"""
    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Name:** {avatar.get('nick_name', 'N/A')}")
        st.info(f"**Type:** {avatar.get('user_type', 'N/A').title()}")

    with col2:
        if avatar.get("self_bio"):
            st.markdown(f"**Description:**")
            st.text(avatar.get("self_bio"))


def filter_tags_by_search(available_tags: list, search_text: str):
    """Filter tags list by search text (case-insensitive)"""
    if not search_text:
        return available_tags
    return [tag for tag in available_tags if search_text.lower() in tag.lower()]


if "model" not in st.session_state:
    st.session_state["model"] = get_model()
    st.success("Model loaded successfully!")

menu = [
    "Welcome Page",
    "Find Projects by Query",
    "Find Projects by Tags",
    "Get Recommendations",
    "View Available Projects",
    "View Project Details",
    "View My Projects",
    "Create Project",
    "Your Avatar",
    "Signup",
    "Login",
    "Profile",
]

choice = st.sidebar.selectbox("Choose an option", menu)

if choice == "Welcome Page":
    st.subheader("Welcome Page")
    st.text("This is the welcome page of Student Projects Recommender System")
elif choice == "Find Projects by Query":
    st.subheader("Find Projects by Query")
    if is_authenticated():
        if is_token_expired():
            st.warning("Session expired. Please login again.")
        else:
            profile = get_user_profile()
            user_id = profile.get("id") if profile else None

            rated_project_ids = get_rated_project_ids(user_id) if user_id else set()

            model = get_model()
            query = st.text_input("Enter approximate project topic")
            if query:
                results = transformer_search(model, query)
                if not results.empty:
                    filtered_results = filter_by_rated_projects(
                        results, rated_project_ids
                    )

                    if filtered_results.empty:
                        st.info(
                            "No new projects found. All similar projects have already been rated."
                        )
                    else:
                        st.markdown("### Similar Projects Found")

                        project_options = create_project_selectbox_options(
                            filtered_results
                        )

                        selected_project_name = st.selectbox(
                            "Select a project to claim as yours",
                            list(project_options.keys()),
                        )

                        if st.button("Claim Selected Project"):
                            if selected_project_name:
                                project_id = project_options[selected_project_name]
                                if claim_project(project_id):
                                    if st.button("Search for Another Project"):
                                        st.rerun()

                        st.markdown("---")
                        st.markdown("#### Available Similar Projects:")
                        for _, row in filtered_results.iterrows():
                            display_search_result(
                                row.get("project", {}),
                                row.get("score", 0),
                                "Similarity",
                            )
                else:
                    st.info("No similar projects found")
    else:
        st.warning("Please login to access this feature")
elif choice == "Get Recommendations":
    st.subheader("Get Recommendations")
    if is_authenticated():
        if is_token_expired():
            st.warning("Session expired. Please login again.")
        else:
            st.markdown(
                "Get personalized project recommendations based on your associated avatar's preferences."
            )

            profile = get_user_profile()
            if not profile:
                st.error("Could not retrieve user profile")
            else:
                user_id = profile.get("id")

                my_avatar = get_my_avatar()

                if not my_avatar:
                    st.warning(
                        "⚠️ No avatar associated. Visit 'Your Avatar' page to select an avatar first."
                    )
                else:
                    avatar_name = my_avatar.get("nick_name", "Unknown")

                    st.info(
                        f"🎭 Using recommendations based on your avatar: **{avatar_name}**"
                    )

                    with st.spinner(
                        "Loading LightFM model and generating recommendations..."
                    ):
                        lightfm_model = get_lightfm_model()

                        if lightfm_model is not None:
                            results = get_lightfm_recommendations(
                                lightfm_model, avatar_name, user_id
                            )

                            if not results.empty:
                                st.success(
                                    f"Found {len(results)} recommendations for you"
                                )

                                project_options = create_project_selectbox_options(
                                    results
                                )

                                selected_project_name = st.selectbox(
                                    "Select a project to claim as yours",
                                    list(project_options.keys()),
                                )

                                if st.button("Claim Selected Project"):
                                    if selected_project_name:
                                        project_id = project_options[
                                            selected_project_name
                                        ]
                                        if claim_project(project_id):
                                            if st.button("Get More Recommendations"):
                                                st.rerun()

                                st.markdown("---")
                                for _, row in results.iterrows():
                                    project = row.get("project", {})
                                    score = row.get("score", 0)
                                    algo = row.get("algo", "unknown")

                                    st.markdown(
                                        f"### {project.get('title_rus', 'Untitled')}"
                                    )
                                    st.caption(f"🎯 {algo.upper()} Score: {score:.2f}")

                                    if project.get("title_eng"):
                                        st.caption(f"🇬🇧 {project.get('title_eng')}")

                                    if project.get("annotation"):
                                        st.info(
                                            f"📝 **Annotation:** {project.get('annotation')}"
                                        )

                                    if project.get("description"):
                                        st.text(project.get("description", ""))

                                    st.markdown("---")
                            else:
                                st.info(
                                    "No new recommendations available. Try selecting a different avatar or rate more projects!"
                                )
                        else:
                            st.error("Could not load LightFM model")
    else:
        st.warning("Please login to access this feature")
elif choice == "Find Projects by Tags":
    st.subheader("Find Projects by Tags")
    if is_authenticated():
        if is_token_expired():
            st.warning("Session expired. Please login again.")
        else:
            profile = get_user_profile()
            user_id = profile.get("id") if profile else None

            rated_project_ids = get_rated_project_ids(user_id) if user_id else set()

            st.markdown(
                "Select multiple tags to find projects with similar tags using cosine similarity."
            )

            available_tags = get_tags_set()

            if not available_tags:
                st.error("No tags available. Please ensure tags_set.pkl file exists.")
            else:
                st.info(f"📋 Available tags: {len(available_tags)}")

                selected_tags = st.multiselect(
                    "Select tags (choose one or more)",
                    options=available_tags,
                    help="Choose multiple tags to find projects with similar tag combinations",
                )

                if selected_tags:
                    st.write(f"✅ Selected tags: {', '.join(selected_tags)}")

                    if (
                        st.button("Find Projects with Similar Tags")
                        or "tags_search_results" in st.session_state
                    ):
                        if not selected_tags:
                            st.error("Please select at least one tag")
                        else:
                            with st.spinner(
                                "Searching for projects with similar tags..."
                            ):
                                tags_vector = compile_tags_vector(selected_tags)
                                results = tags_search(tags_vector=tags_vector)
                                st.session_state["tags_search_results"] = results

                            if not results.empty:
                                filtered_results = filter_by_rated_projects(
                                    results, rated_project_ids
                                )

                                if filtered_results.empty:
                                    st.info(
                                        "No new projects found with these tags. All matching projects have already been rated."
                                    )
                                else:
                                    st.success(
                                        f"Found {len(filtered_results)} projects with similar tags!"
                                    )

                                    project_options = create_project_selectbox_options(
                                        filtered_results
                                    )

                                    selected_project_name = st.selectbox(
                                        "Select a project to claim as yours",
                                        list(project_options.keys()),
                                        key="tags_project_select",
                                    )

                                    if st.button(
                                        "Claim Selected Project",
                                        key="tags_claim_button",
                                    ):
                                        if selected_project_name:
                                            project_id = project_options[
                                                selected_project_name
                                            ]
                                            if claim_project(project_id):
                                                if st.button(
                                                    "Search for Another Project"
                                                ):
                                                    if (
                                                        "tags_search_results"
                                                        in st.session_state
                                                    ):
                                                        del st.session_state[
                                                            "tags_search_results"
                                                        ]
                                                    st.rerun()

                                    st.markdown("---")
                                    for _, row in filtered_results.iterrows():
                                        display_search_result(
                                            row.get("project", {}),
                                            row.get("score", 0),
                                            "Tags Similarity",
                                        )
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
                    project_options = {
                        p.get("title_rus", "Untitled"): p.get("id")
                        for p in all_projects
                    }
                    selected_project = st.selectbox(
                        "Select a project to view details", list(project_options.keys())
                    )

                    if selected_project:
                        project_id = project_options[selected_project]
                        try:
                            response = make_authenticated_request(
                                "GET", f"/projects/{project_id}"
                            )
                            if response.status_code == 200:
                                project = response.json()
                                st.markdown(f"## 📋 Project Details")
                                display_project(project, show_details=True)
                            elif response.status_code == 404:
                                st.error("Project not found")
                            else:
                                st.error(
                                    f"Failed to fetch project: {response.status_code}"
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.info("No projects available to select")
            else:
                st.error(
                    f"Failed to fetch projects list: {projects_response.status_code}"
                )
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
                user_id = profile.get("id")
                if user_id:
                    response = make_authenticated_request(
                        "GET", f"/projects/user/{user_id}"
                    )
                    if response.status_code == 200:
                        projects = response.json()
                        if projects:
                            st.success(f"Found {len(projects)} projects for you")
                            for project in projects:
                                display_project(project)

                                project_id = project.get("id")
                                current_rating = get_project_rating(project_id)

                                st.markdown("### Rate this Project")
                                col1, col2 = st.columns([3, 1])

                                with col1:
                                    new_rating = st.slider(
                                        "Your Rating",
                                        min_value=1,
                                        max_value=5,
                                        value=(
                                            current_rating if current_rating > 0 else 3
                                        ),
                                        step=1,
                                        key=f"rating_{project_id}",
                                    )

                                with col2:
                                    if st.button(
                                        "Submit Rating",
                                        key=f"submit_rating_{project_id}",
                                    ):
                                        if rate_project(project_id, new_rating):
                                            st.rerun()

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

        title_rus = st.text_input(
            "Project Title (Russian)*",
            placeholder="Введите название проекта на русском",
        )
        title_eng = st.text_input(
            "Project Title (English)", placeholder="Enter project title in English"
        )
        annotation = st.text_area(
            "Annotation", placeholder="Short description or summary"
        )
        description = st.text_area(
            "Full Description", placeholder="Detailed description of the project"
        )

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

                    text_data = (
                        text_data.replace("\n", " ")
                        .replace("\r", " ")
                        .replace("\t", " ")
                    )

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
                        "POST", "/projects/", json=project_data
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
                            st.error(response.json().get("detail", "Unknown error"))
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.warning("Please login to access this feature")
elif choice == "Your Avatar":
    st.subheader("Your Avatar")
    if is_authenticated():
        if is_token_expired():
            st.warning("Session expired. Please login again.")
        else:
            profile = get_user_profile()
            user_id = profile.get("id") if profile else None

            st.markdown(
                "## 🎭 Your Avatar Profile\n\n"
                "Avatars are AI-generated persona profiles that help match you with "
                "relevant projects based on similar interests and preferences."
            )

            current_avatar = get_my_avatar()

            if current_avatar:
                st.markdown("### Your Current Avatar")
                display_avatar_info(current_avatar)
                st.markdown("---")

            st.markdown("### Update Your Interests")
            st.info(
                "🏷️ Update your tags to get better avatar recommendations. "
                "The system will find avatars with similar interests based on "
                "cosine similarity of tag vectors."
            )

            available_tags = get_tags_set()

            if not available_tags:
                st.error("No tags available. Please try again later.")
            else:
                response = make_authenticated_request("GET", f"/tags/user/{user_id}")
                current_user_tags = []
                if response.status_code == 200:
                    current_user_tags = [
                        tag.get("tag", {}).get("name") for tag in response.json()
                    ]

                search_tags = st.text_input(
                    "🔍 Search tags",
                    placeholder="Type to filter tags...",
                    key="avatar_tag_search",
                )

                filtered_tags = filter_tags_by_search(available_tags, search_tags)

                selected_tags = st.multiselect(
                    "Select your interests",
                    options=filtered_tags,
                    default=current_user_tags,
                    help="Choose tags that represent your academic interests",
                    key="avatar_tags_update",
                )

                if st.button("Update Tags"):
                    if selected_tags:
                        make_authenticated_request("DELETE", f"/tags/user/{user_id}")
                        if make_authenticated_request(
                            "POST", f"/tags/user/{user_id}", json=selected_tags
                        ):
                            st.success("Tags updated successfully!")
                            st.rerun()
                    else:
                        st.error("Please select at least one tag")

            st.markdown("---")
            st.markdown("### Recommended Avatars")

            with st.spinner("Finding avatars matching your interests..."):
                recommended_avatars = get_avatar_recommendations()

            if recommended_avatars:
                st.success(
                    f"Found {len(recommended_avatars)} avatars matching your interests"
                )

                avatar_options = {
                    f"{a.get('nick_name', 'Unknown')} - {a.get('self_bio', 'No description')[:50]}...": a.get(
                        "id"
                    )
                    for a in recommended_avatars
                }

                selected_avatar_name = st.selectbox(
                    "Select an avatar to view details or associate",
                    list(avatar_options.keys()),
                    key="avatar_select",
                )

                if selected_avatar_name:
                    avatar_id = avatar_options[selected_avatar_name]
                    selected_avatar = next(
                        (a for a in recommended_avatars if a.get("id") == avatar_id),
                        None,
                    )

                    if selected_avatar:
                        st.markdown("#### Avatar Details")
                        display_avatar_info(selected_avatar)

                        if current_avatar and current_avatar.get("id") == avatar_id:
                            st.success("✅ This is your current avatar")
                        else:
                            if st.button(
                                "Associate with this Avatar",
                                key=f"associate_{avatar_id}",
                            ):
                                if select_avatar(avatar_id):
                                    st.success("Avatar associated successfully!")
                                    st.rerun()
            else:
                st.info("No avatars available or could not generate recommendations")

            st.markdown("---")
            st.markdown("### All Available Avatars")

            with st.spinner("Loading all avatars..."):
                all_avatars = get_all_avatars()

            if all_avatars:
                st.info(f"Total avatars available: {len(all_avatars)}")

                for avatar in all_avatars:
                    with st.expander(f"👤 {avatar.get('nick_name', 'Unknown')}"):
                        display_avatar_info(avatar)

                        if current_avatar and current_avatar.get("id") == avatar.get(
                            "id"
                        ):
                            st.success("✅ This is your current avatar")
                        else:
                            if st.button(
                                "Associate with this Avatar",
                                key=f"associate_all_{avatar.get('id')}",
                            ):
                                if select_avatar(avatar.get("id")):
                                    st.success("Avatar associated successfully!")
                                    st.rerun()
    else:
        st.warning("Please login to access this feature")
elif choice == "Signup":
    st.subheader("Signup")
    st.markdown(
        "Create your account to start using the Student Projects Recommender System"
    )

    with st.form("signup_form"):
        st.markdown("### Required Fields")
        nick_name = st.text_input("Username*", placeholder="Choose a unique username")
        password = st.text_input(
            "Password*", type="password", help="Enter a strong password"
        )

        st.markdown("### Personal Information")
        first_name = st.text_input("First Name", placeholder="Your first name")
        middle_name = st.text_input(
            "Middle Name", placeholder="Your middle name (if applicable)"
        )
        last_name = st.text_input("Last Name", placeholder="Your last name")

        st.markdown("### Contact Information")
        email_address = st.text_input(
            "Email Address", placeholder="your.email@example.com"
        )
        phone_number = st.text_input("Phone Number", placeholder="+7 (999) 123-45-67")

        st.markdown("### Additional Information")
        user_type = st.selectbox("User Type", ["student", "teacher", "admin"], index=0)
        self_bio = st.text_area(
            "About Yourself", placeholder="Tell us a bit about yourself...", height=100
        )

        st.markdown("### Your Interests (Tags)")
        st.info(
            "🏷️ Select at least one tag that matches your interests. This helps us recommend relevant projects."
        )

        available_tags = get_tags_set()

        if not available_tags:
            st.error("No tags available. Please try again later.")
        else:
            st.info(f"📋 Available tags: {len(available_tags)}")

            search_tags = st.text_input(
                "🔍 Search tags",
                placeholder="Type to filter tags...",
                key="tag_search",
            )

            filtered_tags = filter_tags_by_search(available_tags, search_tags)

            selected_tags = st.multiselect(
                "Select your interests* (choose at least one)",
                options=filtered_tags,
                help="Choose tags that represent your academic interests and areas of expertise",
                key="signup_tags",
            )

            if selected_tags:
                st.write(f"✅ Selected: {len(selected_tags)} tag(s)")

        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if not nick_name or not password:
                st.error("Please fill in all required fields (marked with *)")
            elif not selected_tags:
                st.error("Please select at least one tag")
            else:
                user_data = {"nick_name": nick_name, "password": password}

                if first_name:
                    user_data["first_name"] = first_name
                if middle_name:
                    user_data["middle_name"] = middle_name
                if last_name:
                    user_data["last_name"] = last_name
                if email_address:
                    user_data["email_address"] = email_address
                if phone_number:
                    user_data["phone_number"] = phone_number
                if user_type:
                    user_data["user_type"] = user_type
                if self_bio:
                    user_data["self_bio"] = self_bio

                signup_success = signup(user_data)
                if signup_success:
                    if login(nick_name, password):
                        profile = get_user_profile()
                        if profile:
                            user_id = profile.get("id")
                            tag_ids = [tag for tag in selected_tags]
                            if add_user_tags(user_id, tag_ids):
                                st.success("Tags added to your profile!")
                                if auto_assign_avatar():
                                    st.success(
                                        "Best matching avatar assigned automatically!"
                                    )
                                st.rerun()
                            else:
                                st.warning(
                                    "Account created but tags could not be added"
                                )
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
            st.markdown("## 👤 Your Profile")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Basic Information")
                st.info(f"**Username:** {profile.get('nick_name', 'N/A')}")
                if (
                    profile.get("first_name")
                    or profile.get("middle_name")
                    or profile.get("last_name")
                ):
                    full_name = " ".join(
                        filter(
                            None,
                            [
                                profile.get("first_name", ""),
                                profile.get("middle_name", ""),
                                profile.get("last_name", ""),
                            ],
                        )
                    )
                    st.info(f"**Full Name:** {full_name}")
                if profile.get("user_type"):
                    st.info(f"**User Type:** {profile.get('user_type', 'N/A').title()}")

            with col2:
                st.markdown("### Contact Information")
                if profile.get("email_address"):
                    st.info(f"**Email:** {profile.get('email_address')}")
                if profile.get("phone_number"):
                    st.info(f"**Phone:** {profile.get('phone_number')}")

            if profile.get("self_bio"):
                st.markdown("### About Me")
                st.text(profile.get("self_bio"))

            st.markdown("---")

            current_avatar = get_my_avatar()
            if current_avatar:
                st.markdown("### 🎭 Your Associated Avatar")
                display_avatar_info(current_avatar)
            else:
                st.info(
                    "🎭 No avatar associated. Visit 'Your Avatar' page to select one."
                )

            st.markdown("---")
            st.markdown("### Account Details")
            if profile.get("created_at"):
                st.caption(f"📅 **Member Since:** {profile.get('created_at')}")
            if profile.get("updated_at"):
                st.caption(f"🔄 **Last Updated:** {profile.get('updated_at')}")
        else:
            st.error("Could not load profile")
    else:
        st.warning("Please login to view your profile")

if is_authenticated() and st.sidebar.button("Logout"):
    logout()
    st.rerun()

if is_authenticated():
    st.sidebar.success(f"Logged in as: {st.session_state.get('username', 'Unknown')}")
