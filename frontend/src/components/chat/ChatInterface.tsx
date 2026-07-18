import { useState, useRef, useEffect } from 'react';
import { Send, Square, Loader2, Plus, Trash2, MessageSquare, RotateCcw } from 'lucide-react';
import { useConversationStore } from '../../stores';
import { ragService } from '../../services';
import type { GenerationRequest, StreamingChunk } from '../../types';

export function ChatInterface() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [showConversationList, setShowConversationList] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const {
    conversations,
    currentConversation,
    messages,
    isStreaming,
    currentResponse,
    startStreaming,
    stopStreaming,
    appendToResponse,
    addMessage,
    clearMessages,
    clearCurrentResponse,
    createConversation,
    loadConversation,
    loadConversations,
    deleteConversation,
    setCurrentConversation,
  } = useConversationStore();

  const suggestedQuestions = [
    'Why did Pump P101 fail?',
    'Show maintenance history for Compressor C204',
    'List all inspections last month',
    'Which SOP applies to Boiler B101?',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentResponse]);

  useEffect(() => {
    // Load conversations on mount
    loadConversations();
  }, [loadConversations]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Add user message
    addMessage({
      id: Date.now(),
      conversation_id: currentConversation?.conversation_id || '',
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    });

    // Create conversation if needed
    let conversationId = currentConversation?.conversation_id;
    if (!conversationId) {
      const conversation = await createConversation(userMessage.slice(0, 50));
      conversationId = conversation.conversation_id;
    }

    // Prepare request
    const request: GenerationRequest = {
      question: userMessage,
      context_package: {
        question: userMessage,
        retrieved_chunks: [],
        entities: [],
        relationships: [],
      },
      conversation_id: conversationId,
    };

    // Start streaming
    startStreaming();
    const controller = new AbortController();
    setAbortController(controller);

    try {
      await ragService.generateAnswerStream(
        request,
        (chunk: StreamingChunk) => {
          if (chunk.chunk) {
            appendToResponse(chunk.chunk);
          }
        },
        (error) => {
          console.error('Streaming error:', error);
          stopStreaming();
          setIsLoading(false);
        },
        () => {
          // Stream complete
          stopStreaming();
          setIsLoading(false);
          
          // Add assistant message
          addMessage({
            id: Date.now(),
            conversation_id: conversationId || '',
            role: 'assistant',
            content: currentResponse,
            created_at: new Date().toISOString(),
          });
          
          clearCurrentResponse();
        }
      );
    } catch (error) {
      console.error('Generation error:', error);
      stopStreaming();
      setIsLoading(false);
      clearCurrentResponse();
    }
  };

  const handleStop = () => {
    abortController?.abort();
    stopStreaming();
    setIsLoading(false);
  };

  const handleNewConversation = async () => {
    const conversation = await createConversation();
    setCurrentConversation(conversation);
    clearMessages();
    setShowConversationList(false);
  };

  const handleSelectConversation = async (conversationId: string) => {
    await loadConversation(conversationId);
    clearMessages();
    setShowConversationList(false);
  };

  const handleDeleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteConversation(conversationId);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-white">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowConversationList(!showConversationList)}
            className="p-2 rounded hover:bg-slate-100 transition-colors"
            aria-label="Toggle conversations"
          >
            <MessageSquare className="h-5 w-5 text-slate-600" />
          </button>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">
              {currentConversation?.title || 'New Conversation'}
            </h2>
            <p className="text-xs text-slate-500">
              {messages.length} messages
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <button
              onClick={() => clearMessages()}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors text-sm"
              title="Clear current chat"
            >
              <RotateCcw className="h-4 w-4" />
              Clear
            </button>
          )}
          <button
            onClick={handleNewConversation}
            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            <Plus className="h-4 w-4" />
            New
          </button>
        </div>
      </div>

      {/* Conversation List Sidebar */}
      {showConversationList && (
        <div className="absolute left-0 top-0 bottom-0 w-64 bg-white border-r border-slate-200 z-10 overflow-y-auto">
          <div className="p-4">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">Conversations</h3>
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.conversation_id}
                  onClick={() => handleSelectConversation(conversation.conversation_id)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    currentConversation?.conversation_id === conversation.conversation_id
                      ? 'bg-blue-50 border border-blue-200'
                      : 'hover:bg-slate-50 border border-transparent'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">
                        {conversation.title || 'Untitled'}
                      </p>
                      <p className="text-xs text-slate-500">
                        {new Date(conversation.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={(e) => handleDeleteConversation(conversation.conversation_id, e)}
                      className="p-1 rounded hover:bg-slate-200 transition-colors"
                      aria-label="Delete conversation"
                    >
                      <Trash2 className="h-3 w-3 text-slate-400" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isStreaming && (
          <div className="text-center text-slate-500 py-12">
            <p className="text-lg mb-2">Start a conversation</p>
            <p className="text-sm mb-6">Ask questions about your industrial documents, equipment, and processes</p>
            <div className="max-w-2xl mx-auto">
              <p className="text-xs font-medium text-slate-400 mb-3">SUGGESTED QUESTIONS</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(question)}
                    className="text-left px-4 py-3 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-sm text-slate-700 transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
          </div>
        ))}

        {isStreaming && currentResponse && (
          <div className="flex justify-start">
            <div className="max-w-2xl rounded-lg px-4 py-3 bg-white border border-slate-200 text-slate-900">
              <p className="whitespace-pre-wrap">{currentResponse}</p>
              <span className="inline-block w-2 h-4 bg-slate-400 ml-1 animate-pulse" />
            </div>
          </div>
        )}

        {isLoading && !isStreaming && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-200 p-4 bg-white">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your industrial knowledge..."
            className="flex-1 resize-none rounded-lg border border-slate-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={2}
            disabled={isLoading}
          />
          <div className="flex flex-col gap-2">
            {isLoading ? (
              <button
                onClick={handleStop}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
              >
                <Square className="h-4 w-4" />
                Stop
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-slate-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Send className="h-4 w-4" />
                Send
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
