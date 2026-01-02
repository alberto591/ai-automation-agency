# ADR-050: RAG & Semantic Matching Strategy for 2026

**Status:** Proposed
**Date:** 2026-01-02
**Author:** Antigravity

**Related**: [ADR-004](0004-rag-credulity-testing.md) (RAG Credulity Testing), [ADR-019](ADR-019-semantic-answer-cache.md) (Semantic Cache)

**Research Document**: [RAG & Matching Study](../reference/architecture/2026-01-02_rag-matching-study.md)

---

## 1. Context (The "Why")

The current property matching system uses basic vector similarity (cosine distance on embeddings) with a fixed 0.78 threshold. While functional for MVP, this approach has limitations:

**Current System Pain Points**:
- **No Relational Context**: Vector search doesn't understand property relationships (e.g., "near metro", "same building")
- **Exact Match Bias**: Struggles with intent-based queries ("spacious for a family" vs. "3 bedrooms")
- **Hallucination Risk**: LLM can fabricate property details when RAG context is weak
- **No Multi-modal Support**: Can't incorporate images, floor plans, or video tours
- **Scalability Issues**: Pure vector search degrades with >100k properties

**Strategic Imperative for 2026**:
- Expand to 10+ cities (currently Milan-focused)
- Support luxury segment (€2M+ properties requiring nuanced matching)
- Enable virtual tours and image-based search
- Reduce hallucination rate from ~15% to <5%

---

## 2. Decision

We propose a **phased implementation** of advanced RAG and matching techniques throughout 2026:

### Phase 1 (Q1 2026): Hybrid Search Foundation
**Timeline**: Jan-Mar 2026

**Implementation**:
1. **Dual-Index Search**:
   - Vector index (pgvector) for semantic similarity
   - Full-text index (PostgreSQL GIN) for keyword precision
   - Hybrid scoring: `score = 0.7 * vector_score + 0.3 * keyword_score`

2. **Contextual Retrieval**:
   - Add property context summaries to chunks
   - Store: `"Property at {address} in {zone}: {description}"`
   - Prevents out-of-context fragment retrieval

3. **Adaptive Thresholds**:
   - Zone-specific thresholds (premium zones: 0.82, suburban: 0.75)
   - Intent-aware: "show me options" → lower threshold, "exact match" → higher

**Expected Impact**: 20-30% reduction in "no results found" cases

---

### Phase 2 (Q2 2026): Property Graph RAG
**Timeline**: Apr-Jun 2026

**Graph Schema**:
```
(Property)-[:LOCATED_IN]->(Zone)
(Property)-[:NEAR]->(POI)  # Points of Interest
(Property)-[:SIMILAR_TO]->(Property)
(Property)-[:LISTED_BY]->(Agency)
(Zone)-[:CONTAINS]->(Street)
```

**Query Pattern**:
```cypher
MATCH (p:Property)-[:LOCATED_IN]->(z:Zone {name: "Centro"})
WHERE p.price < $budget
MATCH (p)-[:NEAR]->(poi:POI) WHERE poi.type IN ["metro", "school"]
RETURN p ORDER BY p.relevance DESC
```

**Benefits**:
- **Relationship Queries**: "Properties near metro in Centro under €500k"
- **Explainability**: Graph path shows why property matched
- **Prevents Hallucinations**: Can't fabricate non-existent relationships

**Tech Stack**: Neo4j or PostgreSQL + Apache AGE extension

**Expected Impact**: 50% reduction in hallucination incidents

---

### Phase 3 (Q3 2026): Multi-modal RAG
**Timeline**: Jul-Sep 2026

**Capabilities**:
1. **Image Embeddings**:
   - CLIP model for floor plan + photo embeddings
   - Query: "modern kitchen with island" matches actual photos
   - Store: 1024-d image vectors alongside text

2. **Virtual Tour Integration**:
   - Matterport 3D tour embeddings
   - Proximity search: "show me properties with similar layouts"

3. **Document Intelligence**:
   - Extract features from PDF listings (energy ratings, cadastral data)
   - OCR + structured extraction via Mistral AI

**Expected Impact**: 40% increase in lead engagement (visual matching)

---

### Phase 4 (Q4 2026): Agentic Matching
**Timeline**: Oct-Dec 2026

**LLM-Powered Reasoning**:
- Move from keyword/vector search to **LLM query generation**
- User: "Investment property for short-term rental"
  - LLM generates: Zone filter (touristic areas), MinBedrooms: 2, Features: ["WiFi", "Central location"]
  - Adds investment criteria: Cap Rate > 4%, ROI > 3%

**ROI-Driven Matching**:
- Not just "what matches criteria" but "what maximizes client value"
- Ranking algorithm: `score = similarity * (1 + investment_quality_score)`

**Expected Impact**: 30% increase in conversion (better aligned recommendations)

---

## 3. Rationale (The "Proof")

### 3.1 Industry Research
- **LangChain Blog (2025)**: Reported 60% reduction in hallucinations with Graph RAG vs. vector-only
- **Pinecone Case Study**: Hybrid search improved recall by 35% for real estate startup
- **OpenAI Retrieval Best Practices**: Recommends contextual chunk prepending (Phase 1)

### 3.2 Competitive Analysis
- **Zillow**: Uses graph-based "similar homes" feature
- **Redfin**: Multi-modal search (text + image) in beta
- **Italian Competitors** (Immobiliare.it, Idealista): Still keyword-only search (opportunity to leapfrog)

### 3.3 Technical Feasibility
- **Supabase pgvector**: Supports hybrid queries via SQL
- **Neo4j Aura**: Free tier sufficient for 100k nodes (properties)
- **Mistral AI**: Native multi-modal support announced Dec 2025

---

## 4. Consequences

### Positive
- ✅ **Market Differentiation**: Only AI agent with graph + multi-modal RAG in Italian market
- ✅ **Scalability**: Graph structure handles 1M+ properties without vector search degradation
- ✅ **Trust**: Explainable results ("matched because near Duomo metro, <10min walk")
- ✅ **Revenue**: Premium tier unlock for luxury segment (€2M+ properties)

### Trade-offs
- ⚠️ **Complexity**: Four distinct search modalities to maintain
- ⚠️ **Cost**: Neo4j hosting ~€200/month, CLIP embeddings compute ~€100/month
- ⚠️ **Data Migration**: Requires backfilling graph for 50k+ existing properties
- ⚠️ **Learning Curve**: Team needs Graph Query Language (Cypher) training

### Risks
- **Over-engineering**: May not need all phases if basic hybrid (Phase 1) solves 90% of cases
  - **Mitigation**: Gate each phase on success metrics (hallucination rate, conversion)
- **Vendor Lock-in**: Neo4j migration costly if needed
  - **Mitigation**: Use PostgreSQL AGE extension (open-source) as alternative

---

## 5. Implementation Roadmap

### Q1 2026 (Phase 1) - Deliverables
- [ ] Migration script: Add full-text GIN index to `properties.title` and `properties.description`
- [ ] `HybridSearchPort` interface in `domain/ports.py`
- [ ] `PostgresHybridAdapter` implementation
- [ ] A/B test: Hybrid vs. vector-only (track "no results" rate)
- [ ] ADR decision point: Proceed to Phase 2 if hallucination rate >10%

### Q2 2026 (Phase 2) - Deliverables
- [ ] Graph schema design + stakeholder review
- [ ] Property → Graph ETL pipeline (Apache Airflow)
- [ ] `GraphRAGPort` interface
- [ ] Neo4j or PostgreSQL AGE adapter
- [ ] Explainability UI: Show graph path in match results

### Q3 2026 (Phase 3) - Deliverables
- [ ] CLIP model integration (Hugging Face or OpenAI)
- [ ] Image embedding pipeline (batch process existing photos)
- [ ] Multi-modal query interface in chatbot
- [ ] Performance optimization (image embeddings are 4x larger)

### Q4 2026 (Phase 4) - Deliverables
- [ ] Agentic query generation (Mistral Large)
- [ ] ROI score integration with investment metrics (ADR-048)
- [ ] Conversion tracking dashboard
- [ ] Whitepa per: "How Anzevino AI Matches Properties"

---

## 6. Wiring Check (No Dead Code)

### Current State (Jan 2026)
- [x] Basic vector search in `DatabasePort.get_properties()`
- [x] 0.78 similarity threshold (ADR-004)
- [x] Semantic cache (ADR-019) reduces redundant searches

### Phase 1 Wiring (Q1 2026)
- [ ] `HybridSearchPort` in domain layer
- [ ] Adapter in `infrastructure/adapters/hybrid_search_adapter.py`
- [ ] Workflow integration in `application/workflows/agents.py` retrieval_node
- [ ] Configuration: `config/settings.py` - `SEARCH_STRATEGY="hybrid"`

### Future Phases
- [ ] Graph adapter wiring (Q2)
- [ ] Multi-modal pipeline (Q3)
- [ ] Agentic query generator (Q4)

---

## 7. Success Metrics

| Metric | Current (Jan 2026) | Target (Dec 2026) |
|--------|-------------------|-------------------|
| Hallucination Rate | ~15% | <5% |
| "No Results" Rate | ~25% | <10% |
| Avg. Properties/Query | 3.2 | 5.0 |
| Lead Conversion (Matches → Viewings) | 12% | 20% |
| Query Latency (p95) | 850ms | <1200ms |

**Decision Gates**:
- Phase 1 → Phase 2: Only if hallucination rate >10% after Q1
- Phase 2 → Phase 3: Only if luxury segment adoption >30 leads/month
- Phase 3 → Phase 4: Only if image search engagement >40%

---

## 8. References

- [Research Study](../reference/architecture/2026-01-02_rag-matching-study.md) - Full analysis
- [LangChain Graph RAG Guide](https://blog.langchain.dev/graph-rag/)
- [Pinecone Hybrid Search](https://www.pinecone.io/learn/hybrid-search/)
- [Neo4j Real Estate Use Cases](https://neo4j.com/use-cases/real-estate/)
- [ADR-004](0004-rag-credulity-testing.md) - Original RAG validation
