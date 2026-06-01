# SQLAlchemy Session And Model Boundaries

- Reuse the existing engine and session factory.
- Match the repository's sync or async session style.
- Keep query and model changes close to the existing ownership boundary.
- Avoid adding a second persistence abstraction unless the repo already uses one.
