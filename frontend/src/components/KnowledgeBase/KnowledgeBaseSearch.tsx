import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import {
  Search as SearchIcon,
  TrendingUp as ScoreIcon,
  Article as ArticleIcon
} from '@mui/icons-material';
import axios from 'axios';

interface SearchResult {
  document_id: string;
  content: string;
  score: number;
  rank: number;
  metadata: any;
}

interface KnowledgeBaseSearchProps {
  open: boolean;
  kbName: string;
  onClose: () => void;
}

const KnowledgeBaseSearch: React.FC<KnowledgeBaseSearchProps> = ({
  open,
  kbName,
  onClose
}) => {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('hybrid');
  const [k, setK] = useState(5);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('请输入搜索内容');
      return;
    }

    setSearching(true);
    setError(null);

    try {
      const response = await axios.post(`/api/knowledge-base/${kbName}/search`, {
        query: query.trim(),
        mode,
        k
      });

      setResults(response.data);
    } catch (err: any) {
      console.error('Search failed:', err);
      setError(err.response?.data?.detail || '搜索失败');
    } finally {
      setSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const getModeLabel = (mode: string) => {
    const labels: Record<string, string> = {
      semantic: '语义搜索',
      keyword: '关键词搜索',
      hybrid: '混合搜索',
      rerank: '重排序搜索'
    };
    return labels[mode] || mode;
  };

  const getModeColor = (mode: string) => {
    const colors: Record<string, any> = {
      semantic: 'primary',
      keyword: 'secondary',
      hybrid: 'success',
      rerank: 'warning'
    };
    return colors[mode] || 'default';
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SearchIcon />
          <Typography variant="h6">搜索知识库: {kbName}</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        {/* Search Input */}
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            multiline
            rows={2}
            variant="outlined"
            label="搜索内容"
            placeholder="输入你想搜索的内容..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{ mb: 2 }}
          />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>搜索模式</InputLabel>
              <Select
                value={mode}
                label="搜索模式"
                onChange={(e) => setMode(e.target.value)}
              >
                <MenuItem value="semantic">语义搜索</MenuItem>
                <MenuItem value="keyword">关键词搜索</MenuItem>
                <MenuItem value="hybrid">混合搜索</MenuItem>
                <MenuItem value="rerank">重排序搜索</MenuItem>
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>返回数量</InputLabel>
              <Select
                value={k}
                label="返回数量"
                onChange={(e) => setK(Number(e.target.value))}
              >
                <MenuItem value={3}>3 条</MenuItem>
                <MenuItem value={5}>5 条</MenuItem>
                <MenuItem value={10}>10 条</MenuItem>
                <MenuItem value={20}>20 条</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="contained"
              startIcon={searching ? <CircularProgress size={20} /> : <SearchIcon />}
              onClick={handleSearch}
              disabled={searching}
              sx={{ ml: 'auto' }}
            >
              {searching ? '搜索中...' : '搜索'}
            </Button>
          </Box>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Results */}
        {results.length > 0 && (
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <ArticleIcon />
              找到 {results.length} 个结果
              <Chip 
                label={getModeLabel(mode)} 
                size="small" 
                color={getModeColor(mode)}
                sx={{ ml: 1 }}
              />
            </Typography>

            {results.map((result, index) => (
              <Card 
                key={result.document_id} 
                sx={{ 
                  mb: 2,
                  transition: 'all 0.2s',
                  '&:hover': {
                    boxShadow: 4,
                    transform: 'translateX(4px)'
                  }
                }}
              >
                <CardContent>
                  {/* Header */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip 
                        label={`#${result.rank}`} 
                        size="small" 
                        color="primary"
                      />
                      <Typography variant="caption" color="text.secondary">
                        {result.document_id}
                      </Typography>
                    </Box>
                    <Chip
                      icon={<ScoreIcon />}
                      label={`相关度: ${(result.score * 100).toFixed(1)}%`}
                      size="small"
                      color={result.score > 0.7 ? 'success' : result.score > 0.4 ? 'warning' : 'default'}
                    />
                  </Box>

                  <Divider sx={{ my: 1 }} />

                  {/* Content */}
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      whiteSpace: 'pre-wrap',
                      backgroundColor: 'background.default',
                      p: 1.5,
                      borderRadius: 1,
                      fontFamily: 'monospace',
                      fontSize: '0.9rem'
                    }}
                  >
                    {result.content}
                  </Typography>

                  {/* Metadata */}
                  {result.metadata && Object.keys(result.metadata).length > 0 && (
                    <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {Object.entries(result.metadata).slice(0, 5).map(([key, value]) => (
                        <Chip
                          key={key}
                          label={`${key}: ${String(value).substring(0, 20)}`}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            ))}
          </Box>
        )}

        {/* Empty State */}
        {!searching && results.length === 0 && query && !error && (
          <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
            <SearchIcon sx={{ fontSize: 48, opacity: 0.3, mb: 2 }} />
            <Typography variant="body1">
              没有找到相关结果
            </Typography>
            <Typography variant="body2">
              尝试使用不同的关键词或搜索模式
            </Typography>
          </Box>
        )}

        {/* Initial State */}
        {!searching && results.length === 0 && !query && (
          <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
            <SearchIcon sx={{ fontSize: 48, opacity: 0.3, mb: 2 }} />
            <Typography variant="body1" gutterBottom>
              输入搜索内容开始
            </Typography>
            <Typography variant="body2">
              支持语义搜索、关键词搜索、混合搜索和重排序搜索
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>关闭</Button>
      </DialogActions>
    </Dialog>
  );
};

export default KnowledgeBaseSearch;
