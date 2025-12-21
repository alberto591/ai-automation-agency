-- Create the storage bucket for chat attachments
insert into storage.buckets (id, name, public)
values ('chat-attachments', 'chat-attachments', true);

-- Policy to allow anyone (anon) to upload files
create policy "Allow public uploads"
on storage.objects for insert
with check ( bucket_id = 'chat-attachments' );

-- Policy to allow anyone to view files
create policy "Allow public viewing"
on storage.objects for select
using ( bucket_id = 'chat-attachments' );

-- Optional: Policy to allow anyone to update their own files (if needed)
-- In this case, we just allow public access for the prototype.
