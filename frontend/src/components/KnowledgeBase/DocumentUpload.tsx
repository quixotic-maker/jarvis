import React, { useState, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Paper
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import axios from 'axios';

interface FileWithStatus {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
  documentIds?: string[];
}

interface DocumentUploadProps {
  open: boolean;
  kbName: string;
  onClose: () => void;
  onSuccess?: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  open,
  kbName,
  onClose,
  onSuccess
}) => {
  const [files, setFiles] = useState<FileWithStatus[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    const newFiles: FileWithStatus[] = selectedFiles.map(file => ({
      file,
      status: 'pending',
      progress: 0
    }));
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer.files);
    const newFiles: FileWithStatus[] = droppedFiles.map(file => ({
      file,
      status: 'pending',
      progress: 0
    }));
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const handleRemoveFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    setUploading(true);

    for (let i = 0; i < files.length; i++) {
      const fileWithStatus = files[i];
      
      if (fileWithStatus.status !== 'pending') {
        continue;
      }

      // Update status to uploading
      setFiles(prev => prev.map((f, idx) => 
        idx === i ? { ...f, status: 'uploading' as const, progress: 0 } : f
      ));

      try {
        const formData = new FormData();
        formData.append('file', fileWithStatus.file);
        formData.append('metadata', JSON.stringify({
          filename: fileWithStatus.file.name,
          uploaded_at: new Date().toISOString()
        }));

        const response = await axios.post(
          `/api/knowledge-base/${kbName}/upload`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const progress = progressEvent.total
                ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
                : 0;
              setFiles(prev => prev.map((f, idx) =>
                idx === i ? { ...f, progress } : f
              ));
            }
          }
        );

        // Success
        setFiles(prev => prev.map((f, idx) =>
          idx === i ? {
            ...f,
            status: 'success' as const,
            progress: 100,
            documentIds: response.data.document_ids
          } : f
        ));
      } catch (error: any) {
        console.error('Upload failed:', error);
        setFiles(prev => prev.map((f, idx) =>
          idx === i ? {
            ...f,
            status: 'error' as const,
            error: error.response?.data?.detail || '上传失败'
          } : f
        ));
      }
    }

    setUploading(false);
    if (onSuccess) {
      onSuccess();
    }
  };

  const getFileIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <FileIcon />;
    }
  };

  const getStatusText = (fileWithStatus: FileWithStatus) => {
    switch (fileWithStatus.status) {
      case 'uploading':
        return `上传中... ${fileWithStatus.progress}%`;
      case 'success':
        return `已上传 (${fileWithStatus.documentIds?.length || 0} 个文档块)`;
      case 'error':
        return fileWithStatus.error || '上传失败';
      default:
        return '等待上传';
    }
  };

  const pendingCount = files.filter(f => f.status === 'pending').length;
  const successCount = files.filter(f => f.status === 'success').length;
  const errorCount = files.filter(f => f.status === 'error').length;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>上传文档到: {kbName}</DialogTitle>

      <DialogContent>
        {/* Drop Zone */}
        <Paper
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          sx={{
            p: 4,
            mb: 2,
            textAlign: 'center',
            border: '2px dashed',
            borderColor: 'divider',
            backgroundColor: 'background.default',
            cursor: 'pointer',
            transition: 'all 0.3s',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'action.hover'
            }
          }}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body1" gutterBottom>
            拖拽文件到这里或点击上传
          </Typography>
          <Typography variant="caption" color="text.secondary">
            支持 TXT, MD, PDF, Python, JavaScript 等格式
          </Typography>
          <input
            id="file-input"
            type="file"
            multiple
            accept=".txt,.md,.pdf,.py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.h"
            style={{ display: 'none' }}
            onChange={handleFileSelect}
          />
        </Paper>

        {/* File List */}
        {files.length > 0 && (
          <>
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <Alert severity="info" sx={{ flex: 1 }}>
                {pendingCount} 待上传 | {successCount} 成功 | {errorCount} 失败
              </Alert>
            </Box>

            <List>
              {files.map((fileWithStatus, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    fileWithStatus.status === 'pending' && !uploading && (
                      <IconButton
                        edge="end"
                        onClick={() => handleRemoveFile(index)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    )
                  }
                >
                  <ListItemIcon>
                    {getFileIcon(fileWithStatus.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={fileWithStatus.file.name}
                    secondary={
                      <>
                        {getStatusText(fileWithStatus)}
                        {fileWithStatus.status === 'uploading' && (
                          <LinearProgress
                            variant="determinate"
                            value={fileWithStatus.progress}
                            sx={{ mt: 1 }}
                          />
                        )}
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}

        {/* Empty State */}
        {files.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 2, color: 'text.secondary' }}>
            <Typography variant="body2">
              还没有选择文件
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>关闭</Button>
        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={uploading || pendingCount === 0}
          startIcon={<UploadIcon />}
        >
          {uploading ? '上传中...' : `上传 (${pendingCount})`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentUpload;
