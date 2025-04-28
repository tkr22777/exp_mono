-- Create Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    author TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Set up Row Level Security (RLS) for the messages table
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create policy for selecting messages (anyone can read all messages)
CREATE POLICY "Anyone can read all messages" 
ON messages FOR SELECT USING (true);

-- Create policy for inserting messages (authenticated users only)
CREATE POLICY "Authenticated users can insert messages" 
ON messages FOR INSERT TO authenticated USING (true) WITH CHECK (auth.uid() = user_id);

-- Create policy for updating messages (only message owners)
CREATE POLICY "Users can update their own messages" 
ON messages FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Create policy for deleting messages (only message owners)
CREATE POLICY "Users can delete their own messages" 
ON messages FOR DELETE TO authenticated USING (auth.uid() = user_id);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS messages_user_id_idx ON messages (user_id);

-- Create index on created_at for faster sorting
CREATE INDEX IF NOT EXISTS messages_created_at_idx ON messages (created_at DESC); 