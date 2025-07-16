# DataAptor AI - Detailed Architecture Diagram

```mermaid
graph TD
    %% User
    User((User))
    style User color:#000,stroke:#333,stroke-width:1px;
    
    %% Client Layer
    subgraph ClientLayer["Client Layer"]
        WebUI["Web UI\n(React.js, Tailwind CSS, Chart.js)\nDashboard, Upload Wizard, Configuration, Results"]
        CLI["CLI\n(Python Click)"]
    end
    
    %% Application Layer
    subgraph ApplicationLayer["Application Layer"]
        APIGateway["API Gateway\n(FastAPI)\nAuth, Rate Limiting, Routing"]
        AuthService["Authentication Service\n(Keycloak)\nRBAC, JWT"]
        OrchestrationService["Orchestration Service\n(FastAPI)\nWorkflow Management"]
    end
    
    %% Processing Layer
    subgraph ProcessingLayer["Processing Layer"]
        IngestionService["Ingestion Service\n(Python, pandas, jq/lxml, NLTK/OpenCV/librosa)\nFile Validation, Metadata Extraction"]
        
        subgraph AssessmentService["Assessment Service (Python)"]
            DataQualityModule["Data Quality Module\nCompleteness, Accuracy, Consistency, Timeliness"]
            AccessibilityModule["Accessibility Module\nAvailability, Volume"]
            GovernanceModule["Governance Module\nPrivacy, Licensing"]
            AICompatibilityModule["AI Compatibility Module\nRelevance, Labeling, Feature Richness, Preprocessing"]
            DiversityModule["Diversity/Bias Module\nRepresentativeness, Diversity"]
        end
        
        ScoringService["Scoring Service\n(Python)\nWeighted Criteria Evaluation"]
        ReportingService["Reporting Service\n(Python, Chart.js)\nScore Breakdowns, Visualizations, Recommendations"]
    end
    
    %% Data Storage Layer
    subgraph DataStorageLayer["Data Storage Layer"]
        MetadataDB["Metadata DB\n(PostgreSQL)"]
        TempStorage["Temporary Storage\n(AWS S3)"]
        ReportStorage["Report Storage\n(AWS S3)"]
    end
    
    %% External Integrations Layer
    subgraph ExternalIntegrationsLayer["External Integrations Layer"]
        CloudStorage["Cloud Storage\n(S3/GCP/Azure)"]
        ExternalDB["External DB\n(MySQL/PostgreSQL/MongoDB)"]
        AIPipelines["AI/ML Pipelines\n(TensorFlow/PyTorch/SageMaker)"]
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
    classDef clientLayer fill:#f9f,stroke:#333,stroke-width:2px,color:#000;
    classDef applicationLayer fill:#bbf,stroke:#333,stroke-width:2px,color:#000;
    classDef processingLayer fill:#bfb,stroke:#333,stroke-width:2px,color:#000;
    classDef assessmentModules fill:#dfd,stroke:#333,stroke-width:1px,color:#000;
    classDef dataStorageLayer fill:#fbb,stroke:#333,stroke-width:2px,color:#000;
    classDef externalLayer fill:#fdb,stroke:#333,stroke-width:2px,color:#000;
    %% Adding a style for the subgraphs to ensure text visibility
    style AssessmentService color:#000;
    style ClientLayer color:#000;
    style ApplicationLayer color:#000;
    style ProcessingLayer color:#000;
    style DataStorageLayer color:#000;
    style ExternalIntegrationsLayer color:#000;
    
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
