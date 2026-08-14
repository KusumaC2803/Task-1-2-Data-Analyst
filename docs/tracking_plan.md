# PlaceMux Marketplace Tracking Plan

| Event | Trigger | Actor | Entity | Purpose |
|---|---|---|---|---|
| company_signed_up | Company completes signup | Company | Company | Measure onboarding |
| company_profile_completed | Profile completed | Company | Company | Measure activation |
| job_created | Job is created | Company | Job | Measure supply creation |
| job_published | Job becomes active | Company | Job | Measure marketplace supply |
| candidate_search | Candidate searches jobs | Candidate | Search | Measure discovery |
| job_viewed | Candidate opens job | Candidate | Job | Measure visibility |
| candidate_applied | Candidate applies | Candidate | Job | Measure demand |
| candidate_shortlisted | Company shortlists candidate | Company | Application | Measure matching quality |
| candidate_rejected | Company rejects application | Company | Application | Understand funnel loss |
| candidate_hired | Company hires candidate | Company | Application | Measure marketplace success |

## Event Flow

Company signup
→ Job creation
→ Job publication
→ Candidate discovery
→ Job view
→ Application
→ Shortlist
→ Hire

## Required Event Properties

Each event contains:

- event name
- actor type
- actor ID
- entity type
- entity ID
- timestamp
- optional event properties

## Privacy

Analytics events use internal identifiers rather than unnecessary personal information.
Sensitive personal information is not required for the marketplace analytics layer.