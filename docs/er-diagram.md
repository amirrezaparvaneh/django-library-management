# Entity Relationship Diagram

## Version 1: Core Book Management
```mermaid
erDiagram
BOOK {
bigint id PK
varchar title
varchar author
varchar isbn UK
smallint publication_year
text description
boolean is_available
datetime created_at
datetime updated_at
}

## Explanation

- `id` is the primary key.
- `title` stores the book title.
- `author` stores the author's name.
- `isbn` stores the book ISBN and should be unique when provided.
- `publication_year` stores the publication year.
- `description` stores optional details.
- `is_available` indicates whether the book is currently available.
- `created_at` stores the creation timestamp.
- `updated_at` stores the last modification timestamp.

## Relationships

Version 1 contains only the `Book` entity, so there are no relationships between entities yet.
