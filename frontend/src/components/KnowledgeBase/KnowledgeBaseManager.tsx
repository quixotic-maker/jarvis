import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Chip,
  LinearProgress,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Folder as FolderIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Upload as UploadIcon,
  Article as ArticleIcon
} from '@mui/icons-material';
import axios from 'axios';
import KnowledgeBaseSearch from './KnowledgeBaseSearch';
import DocumentUpload from './DocumentUpload';

const API_BASE = '/api/knowledge-base';

interface KnowledgeBase {
  name: string;
  description: string;
  document_count: number;
  metadata: any;
}

const KnowledgeBaseManager: React.FC = () => {
  // State
  const [knowledgeBases, setKnowledgeBases] = useState<string[]>([]);
  const [kbInfo, setKbInfo] = useState<Map<string, KnowledgeBase>>(new Map());
  const [loading, setLoading] = useState(false);
  const [selectedKB, setSelectedKB] = useState<string | null>(null);
  
  // Dialog state
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newKBName, setNewKBName] = useState('');
  const [newKBDescription, setNewKBDescription] = useState('');
  const [searchDialogOpen, setSearchDialogOpen] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [searchKBName, setSearchKBName] = useState('');
  
  // Snackbar
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  // Load knowledge bases
  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  const loadKnowledgeBases = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/`);
      const kbNames = response.data;
      setKnowledgeBases(kbNames);
      
      // Load info for each KB
      const infoMap = new Map();
      for (const name of kbNames) {
        try {
          const infoResponse = await axios.get(`${API_BASE}/${name}`);
          infoMap.set(name, infoResponse.data);
        } catch (error) {
          console.error(`Failed to load info for ${name}:`, error);
        }
      }
      setKbInfo(infoMap);
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
      showSnackbar('加载知识库失败', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKB = async () => {
    if (!newKBName.trim()) {
      showSnackbar('请输入知识库名称', 'error');
      return;
    }

    try {
      await axios.post(`${API_BASE}/`, {
        name: newKBName,
        description: newKBDescription,
        chunk_size: 800,
        chunk_overlap: 150
      });
      
      showSnackbar('知识库创建成功', 'success');
      setCreateDialogOpen(false);
      setNewKBName('');
      setNewKBDescription('');
      loadKnowledgeBases();
    } catch (error) {
      console.error('Failed to create KB:', error);
      showSnackbar('创建知识库失败', 'error');
    }
  };

  const handleDeleteKB = async (kbName: string) => {
    if (!window.confirm(`确定要清空知识库 "${kbName}" 吗？`)) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/${kbName}`);
      showSnackbar('知识库已清空', 'success');
      loadKnowledgeBases();
    } catch (error) {
      console.error('Failed to delete KB:', error);
      showSnackbar('删除失败', 'error');
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          📚 知识库管理
        </Typography>
        <Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={loadKnowledgeBases}
            sx={{ mr: 2 }}
          >
            刷新
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            创建知识库
          </Button>
        </Box>
      </Box>

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Knowledge Base Grid */}
      <Grid container spacing={3}>
        {knowledgeBases.map((kbName) => {
          const info = kbInfo.get(kbName);
          return (
            <Grid item xs={12} sm={6} md={4} key={kbName}>
              <Card 
                sx={{ 
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                  },
                  border: selectedKB === kbName ? '2px solid primary.main' : 'none'
                }}
                onClick={() => setSelectedKB(kbName)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <FolderIcon color="primary" sx={{ mr: 1, fontSize: 32 }} />
                    <Typography variant="h6" component="div">
                      {kbName}
                    </Typography>
                  </Box>

                  {info && (
                    <>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {info.description || '暂无描述'}
                      </Typography>

                      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                        <Chip
                          icon={<ArticleIcon />}
                          label={`${info.document_count} 文档`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Box>

                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          startIcon={<SearchIcon />}
                          variant="outlined"
                          fusetSearchKBName(kbName);
                            setSearchDialogOpen(true);
                          }}
                        >
                          搜索
                        </Button>
                        <Button
                          size="small"
                          startIcon={<UploadIcon />}
                          variant="outlined"
                          fullWidth
                          onClick={(e) => {
                            e.stopPropagation();
                            setSearchKBName(kbName);
                            setUploadDialogOpen(true);
                          onClick={(e) => {
                            e.stopPropagation();
                            // TODO: 打开上传对话框
                          }}
                        >
                          上传
                        </Button>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteKB(kbName);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </>
                  )}
                </CardContent>
              </Card>
            </Grid>
          );
        })}

        {/* Empty State */}
        {!loading && knowledgeBases.length === 0 && (
          <Grid item xs={12}>
            <Box 
              sx={{ 
                textAlign: 'center', 
                py: 8,
                color: 'text.secondary'
              }}
            >
              <FolderIcon sx={{ fontSize: 64, opacity: 0.3, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                还没有知识库
              </Typography>
              <Typography variant="body2" sx={{ mb: 3 }}>
                创建第一个知识库开始管理你的文档
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
              >
                创建知识库
              </Button>
            </Box>
          </Grid>
        )}
      </Grid>

      {/* Create Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>创建知识库</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="知识库名称"
            type="text"
            fullWidth
            variant="outlined"
            value={newKBName}
            onChange={(e) => setNewKBName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="描述（可选）"
            type="text"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={newKBDescription}
            onChange={(e) => setNewKBDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>取消</Button>
          <Button onClick={handleCreateKB} variant="contained">
            创建
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}

      {/* Search Dialog */}
      <KnowledgeBaseSearch
        open={searchDialogOpen}
        kbName={searchKBName}
        onClose={() => setSearchDialogOpen(false)}
      />

      {/* Upload Dialog */}
      <DocumentUpload
        open={uploadDialogOpen}
        kbName={searchKBName}
        onClose={() => setUploadDialogOpen(false)}
        onSuccess={loadKnowledgeBases}
      />
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default KnowledgeBaseManager;
