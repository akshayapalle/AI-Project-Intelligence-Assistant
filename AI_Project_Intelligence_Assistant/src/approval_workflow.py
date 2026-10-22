
import streamlit as st

from src.memory_store import get_connection


def initialize_approval_db():
    """Create a persistent change-request table and seed known requests."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS change_requests (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL DEFAULT '',
                    owner TEXT NOT NULL DEFAULT 'Unassigned',
                    status TEXT NOT NULL DEFAULT 'Pending Approval'
                        CHECK (
                            status IN (
                                'Pending Approval',
                                'Approved',
                                'Rejected'
                            )
                        ),
                    source_note TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                INSERT INTO change_requests
                    (title, description, owner, status, source_note)
                VALUES
                    (
                        'OTP Login (CR001)',
                        'OTP login was recorded as a change request and was '
                        'not approved for implementation in the source documents.',
                        'Rahul',
                        'Pending Approval',
                        'Source documents: meeting_01_2026-10-02.docx; '
                        'update_02_2026-10-02.txt'
                    ),
                    (
                        'Google Login',
                        'Google login was approved for implementation. '
                        'The official Sprint 1 deadline reassessment remains pending.',
                        'Ananya (PM)',
                        'Approved',
                        'Source documents: update_10_2026-10-08.txt; '
                        'meeting_02_2026-10-05.docx'
                    )
                ON CONFLICT (title) DO NOTHING;
            """)


def show_approval_workflow():
    st.subheader("Change Request Approval")

    try:
        initialize_approval_db()

        with st.form("change_request_form", clear_on_submit=True):
            title = st.text_input("Change request title")
            description = st.text_area("Description")
            owner = st.text_input("Assigned owner")

            submitted = st.form_submit_button("Add Change Request")

            if submitted:
                if not title.strip():
                    st.warning("Please enter a change request title.")
                else:
                    with get_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO change_requests
                                    (title, description, owner)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (title) DO NOTHING
                                RETURNING id;
                            """, (
                                title.strip(),
                                description.strip(),
                                owner.strip() or "Unassigned",
                            ))
                            inserted = cur.fetchone()

                    if inserted:
                        st.success("Change request saved to PostgreSQL.")
                    else:
                        st.warning(
                            "A request with that title already exists."
                        )

                    st.rerun()

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, owner, status, source_note
                    FROM change_requests
                    ORDER BY id;
                """)
                requests = cur.fetchall()

        if not requests:
            st.info("No change requests found.")
            return

        for request in requests:
            request_id, title, description, owner, status, source_note = request

            with st.expander(title):
                st.write("**Description:**", description or "Not provided")
                st.write("**Owner:**", owner)
                st.write("**Status:**", status)

                if source_note:
                    st.caption(source_note)

                statuses = [
                    "Pending Approval",
                    "Approved",
                    "Rejected",
                ]

                new_status = st.selectbox(
                    "Update status",
                    statuses,
                    index=statuses.index(status),
                    key=f"approval_status_{request_id}",
                )

                if st.button(
                    "Save Status",
                    key=f"save_approval_{request_id}",
                ):
                    with get_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE change_requests
                                SET status = %s, updated_at = NOW()
                                WHERE id = %s;
                            """, (new_status, request_id))

                    st.success("Status saved to PostgreSQL.")
                    st.rerun()

    except Exception as error:
        st.error(f"Approval workflow error: {error}")
