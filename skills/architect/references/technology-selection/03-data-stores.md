# Data Stores

Choosing storage by data lifecycle and query shape: relational as the default source of truth; search/analytical/vector as read models. Use for primary-storage selection, read/write splitting, RAG storage design, and judging when to split stores.

## Do not make one database carry every problem

At MVP, one relational store carrying transactions, reports, search, attachments, and vectors is fine. The problem arrives when the business grows and these data classes diverge completely in access pattern: orders need strong consistency and zero loss; reports scan masses of history without dragging the primary store; search needs relevance ranking, not `LIKE`; images and video need cheap storage with CDN delivery; RAG needs vector recall plus permission filtering.

The architectural judgment is not "which database is best" but **which storage model should carry which data class**. A system often needs several stores, but each one adds synchronization paths, consistency boundaries, operational work, and debugging cost.

## Draw the data lifecycle first

Before choosing a database, draw one data class from birth to archive: write → validate → commit → query/retrieve → analyze/report → archive/delete. Answer five questions:

| Question | Why it matters |
| --- | --- |
| Read-heavy or write-heavy | Decides read/write splitting, caching, index model |
| Where is the transaction boundary | Decides whether relational transactions can enclose it |
| What is the query shape | Primary-key lookup, range, full-text, vector similarity—completely different |
| How fast does data grow | Decides partitioning, hot/cold tiering, archiving strategy |
| What happens on corruption | Decides consistency, backup, audit, and recovery levels |

Size the data, the read/write ratio, and the retention period before talking tools.

## Primary storage: relational is still the default start

| Type | Fits | Does not fit |
| --- | --- | --- |
| Relational (PostgreSQL, MySQL) | Transactions, orders, permissions, tenants, ledgers—data needing transactions | Extreme-scale analytics, full-text search, masses of unstructured files |
| Document (MongoDB) | Frequently changing structure, whole-document read/write, weakly related data | Strong transactions, complex multi-table joins, strict reporting |
| Key-value (DynamoDB, persistent Redis) | High-speed key read/write, simple structure, extreme scale | Complex queries, flexible joins |
| Columnar/analytical (ClickHouse, BigQuery) | Reports, aggregation, log analysis, behavior analysis | High-frequency small transactional writes |

Default advice: first stabilize core transactional data in a relational store; only when reports, search, logs, or vector retrieval genuinely become independent pressure do you split out the corresponding read model. Do not stuff each data class into a different database on day one for the sake of modernity.

## Read models are not accessories of the primary store

When the query shape departs from what the primary store is good at, consider a read model:

| Need | Common engines | Key tradeoff |
| --- | --- | --- |
| Full-text search | Elasticsearch, OpenSearch, Meilisearch | Buys relevance and inverted indexes; the price is index-sync maintenance and eventual consistency |
| Report analytics | ClickHouse, BigQuery, Snowflake | Columnar scans and aggregation are fast, but they cannot carry transactional writes in return |
| Object storage | S3, OSS, GCS | Cheap, durable file storage—but do not query it like a database |
| Vector database | Milvus, Qdrant, pgvector | Strong similarity retrieval, but permission filtering, recall quality, and cost need evaluation |
| Time-series database | Prometheus, InfluxDB | Strong metric-timeline queries; not for ordinary business objects |

The easiest mistake is treating the read model as the source of truth. The correct relation: primary store = source of truth; search/analytical/vector stores = read models synced from the primary store or object storage. A read model may lag, but you must state clearly **how long it may lag, how to compensate, and how to rebuild**. A user updating their profile writing only to the search index while the primary store knows nothing—that is an incident.

## RAG: a vector store is not the only answer

RAG easily gets flattened into "chunk documents → vector store → topK → LLM answers". A real system also includes: raw-text object storage, parsing and chunking, a metadata primary store, a keyword index (hybrid retrieval), and permission/tenant filtering.

Ask when selecting: is permission filtering done before or after retrieval (post-filtering may under-recall)? Vector-only or hybrid retrieval? Where do raw text and citations live (the vector store should not be the sole source of truth)? If the index breaks, can it be rebuilt from raw text and metadata? Can cost grow linearly with document count and query volume?

A vector store solves similarity recall; it does not solve permissions, source of truth, citations, or evaluation. Do not flatten a RAG system into one store.

## Trigger signals for splitting stores

| Signal | Likely action |
| --- | --- |
| Report queries slowing the transactional store (OLTP/OLAP interference) | Sync to an analytical store |
| Poor search relevance, slow LIKE scans | Build a search index |
| Attachments/images bloating the database | Migrate to object storage + CDN |
| Single-table growth slowing indexes and backups | Partition, archive, hot/cold separation |
| Unstable RAG recall quality | Hybrid retrieval + rerank + eval |

The counter-case: with small data, a small team, and low failure cost, one relational store with sane indexes and regular backups is often healthier than prematurely introducing five stores.

## How to write the selection conclusion

The key is stating clearly **which read model was crushing which source of truth**, not "ClickHouse is fast". Example: context—monthly reports scanning 200 million rows of historical events, transactional P99 rising from 120ms to 900ms; choice—the primary store remains the source of truth, Outbox events sync to an analytical store, reports query only the analytical store; given up—strong real-time reporting, allowing up to 1 minute of lag; gained—isolation of the transactional path from the reporting path; re-review conditions—when reports must become second-level real-time or sync lag exceeds business tolerance, re-evaluate.

## Relationship to other documents

- The consistency engineering of read-model lag and compensation is in [Consistency](../09-consistency.md).
- The general principles of data and state design are in [Data and state](../05-data-and-state.md).
- The unified selection decision tree is in [Selection principles](./01-principles.md).
- The overall design of RAG systems is in [AI system design](../ai/02-ai-system-design.md).
