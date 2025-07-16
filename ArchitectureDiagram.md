# DataAptor AI - Detailed Architecture Diagram

```mermaid
graph TD
    %% User
    User((User))
    
    %% Client Layer
    subgraph ClientLayer["Client Layer"]
        WebUI["Web UI<br>(React.js, Tailwind CSS, Chart.js)<br>Dashboard, Upload Wizard, Configuration, Results"]
        CLI["CLI<br>(Python Click)"]
    end
    
    %% Application Layer
    subgraph ApplicationLayer["Application Layer"]
        APIGateway["API Gateway<br>(FastAPI)<br>Auth, Rate Limiting, Routing"]
        AuthService["Authentication Service<br>(Keycloak)<br>RBAC, JWT"]
        OrchestrationService["Orchestration Service<br>(FastAPI)<br>Workflow Management"]
    end
    
    %% Processing Layer
    subgraph ProcessingLayer["Processing Layer"]
        IngestionService["Ingestion Service<br>(Python, pandas, jq/lxml, NLTK/OpenCV/librosa)<br>File Validation, Metadata Extraction"]
        
        subgraph AssessmentService["Assessment Service (Python)"]
            DataQualityModule["Data Quality Module<br>Completeness, Accuracy, Consistency, Timeliness"]
            AccessibilityModule["Accessibility Module<br>Availability, Volume"]
            GovernanceModule["Governance Module<br>Privacy, Licensing"]
            AICompatibilityModule["AI Compatibility Module<br>Relevance, Labeling, Feature Richness, Preprocessing"]
            DiversityModule["Diversity/Bias Module<br>Representativeness, Diversity"]
        end
        
        ScoringService["Scoring Service<br>(Python)<br>Weighted Criteria Evaluation"]
        ReportingService["Reporting Service<br>(Python, Chart.js)<br>Score Breakdowns, Visualizations, Recommendations"]
    end
    
    %% Data Storage Layer
    subgraph DataStorageLayer["Data Storage Layer"]
        MetadataDB[(Metadata DB<br>(PostgreSQL))]
        TempStorage[("Temporary Storage<br>(AWS S3)")]
        ReportStorage[("Report Storage<br>(AWS S3)")]
    end
    
    %% External Integrations Layer
    subgraph ExternalIntegrationsLayer["External Integrations Layer"]
        CloudStorage[("Cloud Storage<br>(S3/GCP/Azure)")]
        ExternalDB[(External DB<br>(MySQL/PostgreSQL/MongoDB))]
        AIPipelines["AI/ML Pipelines<br>(TensorFlow/PyTorch/SageMaker)"]
        ExternalAPIs["External APIs"]
    end
    
    %% Data Flow
    %% Client to Application Layer
    User -->|HTTPS| WebUI
    User -->|Commands| CLI
    WebUI -->|REST/HTTPS| APIGateway
    CLI -->|REST API| APIGateway
    
    %% Application Layer Flow
    APIGateway <-->|JWT Auth| AuthService
    APIGateway -->|Validated Requests| OrchestrationService
    
    %% Orchestration to Processing Layer
    OrchestrationService -->|Dataset Metadata| IngestionService
    OrchestrationService -->|Triggers Assessment| DataQualityModule
    OrchestrationService -->|Triggers Scoring| ScoringService
    OrchestrationService -->|Triggers Reporting| ReportingService
    
    %% Processing Layer Internal Flow
    IngestionService --> DataQualityModule
    IngestionService --> AccessibilityModule
    IngestionService --> GovernanceModule
    IngestionService --> AICompatibilityModule
    IngestionService --> DiversityModule
    
    DataQualityModule --> ScoringService
    AccessibilityModule --> ScoringService
    GovernanceModule --> ScoringService
    AICompatibilityModule --> ScoringService
    DiversityModule --> ScoringService
    
    ScoringService --> ReportingService
    
    %% Processing to Data Storage
    IngestionService -->|Store Datasets| TempStorage
    IngestionService -->|Store Metadata| MetadataDB
    DataQualityModule -->|Store Results| MetadataDB
    AccessibilityModule -->|Store Results| MetadataDB
    GovernanceModule -->|Store Results| MetadataDB
    AICompatibilityModule -->|Store Results| MetadataDB
    DiversityModule -->|Store Results| MetadataDB
    ScoringService -->|Store Scores| MetadataDB
    ReportingService -->|Store Reports| ReportStorage
    ReportingService -->|Store Metadata| MetadataDB
    
    %% External Integrations
    CloudStorage -->|Dataset Import| IngestionService
    ExternalDB -->|Data Extraction| IngestionService
    ReportingService -->|Export Results| AIPipelines
    ExternalAPIs <-->|REST API| APIGateway
    
    %% Return Flow to Client
    ReportingService -->|Notification| OrchestrationService
    OrchestrationService -->|Results| APIGateway
    APIGateway -->|Response| WebUI
    APIGateway -->|Response| CLI
    
    %% Styling
    classDef clientLayer fill:#f9f,stroke:#333,stroke-width:2px;
    classDef applicationLayer fill:#bbf,stroke:#333,stroke-width:2px;
    classDef processingLayer fill:#bfb,stroke:#333,stroke-width:2px;
    classDef assessmentModules fill:#dfd,stroke:#333,stroke-width:1px;
    classDef dataStorageLayer fill:#fbb,stroke:#333,stroke-width:2px;
    classDef externalLayer fill:#fdb,stroke:#333,stroke-width:2px;
    
    class WebUI,CLI clientLayer;
    class APIGateway,AuthService,OrchestrationService applicationLayer;
    class IngestionService,ScoringService,ReportingService processingLayer;
    class DataQualityModule,AccessibilityModule,GovernanceModule,AICompatibilityModule,DiversityModule assessmentModules;
    class MetadataDB,TempStorage,ReportStorage dataStorageLayer;
    class CloudStorage,ExternalDB,AIPipelines,ExternalAPIs externalLayer;
```

## Viewing the Diagram

To view this Mermaid diagram:
1. Use a Markdown editor that supports Mermaid syntax (like VS Code with Mermaid extension)
2. Or paste the Mermaid code into an online Mermaid editor like [Mermaid Live Editor](https://mermaid.live/)
3. In GitHub, this diagram will render automatically if the repository has Mermaid rendering enabled
