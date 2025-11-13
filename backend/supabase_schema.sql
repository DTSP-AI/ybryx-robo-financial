-- Ybryx Capital - Supabase Schema for Agent Memory & Audit System
-- Follows MEMORY_MANAGEMENT_STANDARD.md and AGENT_JSONCONTRACT1st_IDENTITY-RESPONSE_STNDRD.md

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector for embeddings (if using Mem0 with PGVector backend)
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable Row Level Security
-- (RLS policies will be defined per table)

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table (managed by Supabase Auth, extended with custom fields)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'agent', 'admin', 'system')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create index on email
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- RLS for users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Admins can view all users"
    ON users FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role = 'admin'
        )
    );

-- ============================================================================
-- SESSION MANAGEMENT
-- ============================================================================

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id TEXT UNIQUE NOT NULL, -- External session identifier
    agent_name TEXT NOT NULL,
    client_info JSONB DEFAULT '{}'::jsonb, -- User agent, IP, etc.
    context JSONB DEFAULT '{}'::jsonb, -- Initial context
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed', 'timeout')),
    started_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    ended_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_agent_name ON sessions(agent_name);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at DESC);

-- RLS for sessions
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own sessions"
    ON sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can manage all sessions"
    ON sessions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role IN ('system', 'admin')
        )
    );

-- ============================================================================
-- AGENT EXECUTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    agent_version TEXT DEFAULT '1.0.0',
    execution_id TEXT UNIQUE NOT NULL, -- JSONContract identity
    input_payload JSONB NOT NULL,
    output_payload JSONB,
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'timeout')),
    error_details JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    iteration_count INTEGER DEFAULT 0,
    tool_calls JSONB DEFAULT '[]'::jsonb, -- Array of tool invocations
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_agent_executions_user_id ON agent_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_session_id ON agent_executions(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_name ON agent_executions(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_executions_execution_id ON agent_executions(execution_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_started_at ON agent_executions(started_at DESC);

-- RLS for agent_executions
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own executions"
    ON agent_executions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can manage all executions"
    ON agent_executions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role IN ('system', 'admin')
        )
    );

-- ============================================================================
-- MEMORY LOGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS memory_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    operation_type TEXT NOT NULL CHECK (operation_type IN ('write', 'read', 'recall', 'decay', 'delete')),
    memory_type TEXT NOT NULL CHECK (memory_type IN ('short_term', 'long_term', 'episodic', 'semantic', 'procedural')),
    content TEXT, -- Human-readable content
    vector_id TEXT, -- Reference to Mem0 vector ID
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memory_logs_user_id ON memory_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_logs_session_id ON memory_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_logs_agent_name ON memory_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_memory_logs_operation_type ON memory_logs(operation_type);
CREATE INDEX IF NOT EXISTS idx_memory_logs_memory_type ON memory_logs(memory_type);
CREATE INDEX IF NOT EXISTS idx_memory_logs_timestamp ON memory_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_memory_logs_tags ON memory_logs USING GIN(tags);

-- RLS for memory_logs
ALTER TABLE memory_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own memory logs"
    ON memory_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can manage all memory logs"
    ON memory_logs FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role IN ('system', 'admin')
        )
    );

-- ============================================================================
-- GOAL ASSESSMENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS goal_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    goal_description TEXT NOT NULL,
    goal_vector VECTOR(1536), -- OpenAI embedding dimension
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'achieved', 'abandoned', 'blocked')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    assessment JSONB DEFAULT '{}'::jsonb, -- Structured assessment data
    achieved_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_goal_assessments_user_id ON goal_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_goal_assessments_session_id ON goal_assessments(session_id);
CREATE INDEX IF NOT EXISTS idx_goal_assessments_agent_name ON goal_assessments(agent_name);
CREATE INDEX IF NOT EXISTS idx_goal_assessments_status ON goal_assessments(status);
CREATE INDEX IF NOT EXISTS idx_goal_assessments_priority ON goal_assessments(priority DESC);

-- Vector similarity search index
CREATE INDEX IF NOT EXISTS idx_goal_assessments_vector ON goal_assessments USING ivfflat (goal_vector vector_cosine_ops);

-- RLS for goal_assessments
ALTER TABLE goal_assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own goals"
    ON goal_assessments FOR ALL
    USING (auth.uid() = user_id);

-- ============================================================================
-- BELIEF GRAPHS
-- ============================================================================

CREATE TABLE IF NOT EXISTS belief_graphs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    belief_key TEXT NOT NULL, -- Unique key for the belief
    belief_value TEXT NOT NULL, -- The belief content
    belief_vector VECTOR(1536),
    confidence_score FLOAT DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    source TEXT, -- Origin of the belief
    evidence JSONB DEFAULT '[]'::jsonb, -- Supporting evidence
    related_beliefs TEXT[] DEFAULT ARRAY[]::TEXT[], -- References to other belief_keys
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_belief_graphs_user_id ON belief_graphs(user_id);
CREATE INDEX IF NOT EXISTS idx_belief_graphs_session_id ON belief_graphs(session_id);
CREATE INDEX IF NOT EXISTS idx_belief_graphs_agent_name ON belief_graphs(agent_name);
CREATE INDEX IF NOT EXISTS idx_belief_graphs_belief_key ON belief_graphs(belief_key);
CREATE INDEX IF NOT EXISTS idx_belief_graphs_confidence_score ON belief_graphs(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_belief_graphs_vector ON belief_graphs USING ivfflat (belief_vector vector_cosine_ops);

-- RLS for belief_graphs
ALTER TABLE belief_graphs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own beliefs"
    ON belief_graphs FOR ALL
    USING (auth.uid() = user_id);

-- ============================================================================
-- COGNITIVE METRICS
-- ============================================================================

CREATE TABLE IF NOT EXISTS cognitive_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    metric_type TEXT NOT NULL CHECK (metric_type IN ('attention', 'reasoning_depth', 'creativity', 'efficiency', 'accuracy')),
    metric_value FLOAT NOT NULL,
    context JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cognitive_metrics_user_id ON cognitive_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_cognitive_metrics_session_id ON cognitive_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_cognitive_metrics_agent_name ON cognitive_metrics(agent_name);
CREATE INDEX IF NOT EXISTS idx_cognitive_metrics_metric_type ON cognitive_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_cognitive_metrics_timestamp ON cognitive_metrics(timestamp DESC);

-- RLS for cognitive_metrics
ALTER TABLE cognitive_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own metrics"
    ON cognitive_metrics FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can manage all metrics"
    ON cognitive_metrics FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role IN ('system', 'admin')
        )
    );

-- ============================================================================
-- AUDIT LOGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    agent_name TEXT,
    event_type TEXT NOT NULL, -- e.g., 'memory_write', 'agent_execution', 'goal_update'
    event_category TEXT DEFAULT 'general' CHECK (event_category IN ('general', 'security', 'performance', 'error', 'memory', 'agent')),
    severity TEXT DEFAULT 'info' CHECK (severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}'::jsonb, -- Structured event data
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_session_id ON audit_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_agent_name ON audit_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_category ON audit_logs(event_category);
CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON audit_logs(severity);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- RLS for audit_logs
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view all audit logs"
    ON audit_logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role = 'admin'
        )
    );

CREATE POLICY "System can write audit logs"
    ON audit_logs FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid() AND users.role IN ('system', 'admin')
        )
    );

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goal_assessments_updated_at
    BEFORE UPDATE ON goal_assessments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_belief_graphs_updated_at
    BEFORE UPDATE ON belief_graphs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get active session for user
CREATE OR REPLACE FUNCTION get_active_session(p_user_id UUID, p_agent_name TEXT)
RETURNS UUID AS $$
DECLARE
    v_session_id UUID;
BEGIN
    SELECT id INTO v_session_id
    FROM sessions
    WHERE user_id = p_user_id
      AND agent_name = p_agent_name
      AND status = 'active'
    ORDER BY started_at DESC
    LIMIT 1;

    RETURN v_session_id;
END;
$$ LANGUAGE plpgsql;

-- Function to close session
CREATE OR REPLACE FUNCTION close_session(p_session_id UUID, p_status TEXT DEFAULT 'completed')
RETURNS VOID AS $$
BEGIN
    UPDATE sessions
    SET status = p_status,
        ended_at = NOW()
    WHERE id = p_session_id;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate agent execution duration
CREATE OR REPLACE FUNCTION calculate_execution_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.completed_at IS NOT NULL AND OLD.completed_at IS NULL THEN
        NEW.duration_ms = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at)) * 1000;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_agent_execution_duration
    BEFORE UPDATE ON agent_executions
    FOR EACH ROW
    EXECUTE FUNCTION calculate_execution_duration();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Recent agent activity
CREATE OR REPLACE VIEW recent_agent_activity AS
SELECT
    ae.id,
    ae.agent_name,
    ae.execution_id,
    ae.status,
    ae.started_at,
    ae.duration_ms,
    u.email as user_email,
    s.session_id
FROM agent_executions ae
JOIN users u ON ae.user_id = u.id
JOIN sessions s ON ae.session_id = s.id
ORDER BY ae.started_at DESC;

-- Memory operation summary
CREATE OR REPLACE VIEW memory_operation_summary AS
SELECT
    agent_name,
    operation_type,
    memory_type,
    COUNT(*) as operation_count,
    DATE_TRUNC('day', timestamp) as operation_date
FROM memory_logs
GROUP BY agent_name, operation_type, memory_type, DATE_TRUNC('day', timestamp)
ORDER BY operation_date DESC;

-- User session stats
CREATE OR REPLACE VIEW user_session_stats AS
SELECT
    u.id as user_id,
    u.email,
    COUNT(DISTINCT s.id) as total_sessions,
    COUNT(DISTINCT CASE WHEN s.status = 'active' THEN s.id END) as active_sessions,
    COUNT(DISTINCT ae.id) as total_executions,
    MAX(s.started_at) as last_session_start
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN agent_executions ae ON s.id = ae.session_id
GROUP BY u.id, u.email;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users IS 'Extended user profiles with role management';
COMMENT ON TABLE sessions IS 'Active and historical agent sessions';
COMMENT ON TABLE agent_executions IS 'Individual agent execution records with performance metrics';
COMMENT ON TABLE memory_logs IS 'Audit trail of all memory operations (write, read, recall, decay)';
COMMENT ON TABLE goal_assessments IS 'Agent goal tracking with vector embeddings';
COMMENT ON TABLE belief_graphs IS 'Agent belief system with confidence scoring';
COMMENT ON TABLE cognitive_metrics IS 'Agent performance and cognitive load metrics';
COMMENT ON TABLE audit_logs IS 'Comprehensive system audit trail';

-- ============================================================================
-- GRANTS (adjust based on your service role setup)
-- ============================================================================

-- Grant necessary permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant to service role (for backend access)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
