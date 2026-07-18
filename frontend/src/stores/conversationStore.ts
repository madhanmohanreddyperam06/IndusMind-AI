// Conversation Store - AI Chat State
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Conversation, ConversationMessage } from '../types/rag';

interface ConversationState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: ConversationMessage[];
  isStreaming: boolean;
  currentResponse: string;
  
  // Actions
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  setMessages: (messages: ConversationMessage[]) => void;
  addMessage: (message: ConversationMessage) => void;
  clearMessages: () => void;
  createConversation: (title?: string) => Promise<Conversation>;
  loadConversation: (conversationId: string) => Promise<void>;
  loadConversations: () => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  startStreaming: () => void;
  stopStreaming: () => void;
  appendToResponse: (chunk: string) => void;
  setCurrentResponse: (response: string) => void;
  clearCurrentResponse: () => void;
}

export const useConversationStore = create<ConversationState>()(
  persist(
    (set) => ({
      conversations: [],
      currentConversation: null,
      messages: [],
      isStreaming: false,
      currentResponse: '',

      setConversations: (conversations) => set({ conversations }),

      setCurrentConversation: (conversation) => set({ currentConversation: conversation }),

      setMessages: (messages) => set({ messages }),

      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),

      clearMessages: () => set({ messages: [] }),

      createConversation: async (title?: string) => {
        const { ragService } = await import('../services');
        const conversation = await ragService.createConversation(undefined, title);
        set((state) => ({ conversations: [conversation, ...state.conversations] }));
        return conversation;
      },

      loadConversation: async (conversationId: string) => {
        const { ragService } = await import('../services');
        const conversation = await ragService.getConversation(conversationId);
        set({ currentConversation: conversation });
        // Load messages would go here when backend provides endpoint
      },

      loadConversations: async () => {
        const { ragService } = await import('../services');
        try {
          const conversations = await ragService.getConversations();
          set({ conversations });
        } catch (error) {
          console.error('Failed to load conversations:', error);
          // If endpoint doesn't exist, keep empty array
          set({ conversations: [] });
        }
      },

      deleteConversation: async (conversationId: string) => {
        const { ragService } = await import('../services');
        await ragService.deleteConversation(conversationId);
        set((state) => ({
          conversations: state.conversations.filter((c) => c.conversation_id !== conversationId),
          currentConversation: state.currentConversation?.conversation_id === conversationId ? null : state.currentConversation,
        }));
      },

      startStreaming: () => set({ isStreaming: true, currentResponse: '' }),

      stopStreaming: () => set({ isStreaming: false }),

      appendToResponse: (chunk) => set((state) => ({ currentResponse: state.currentResponse + chunk })),

      setCurrentResponse: (response) => set({ currentResponse: response }),

      clearCurrentResponse: () => set({ currentResponse: '' }),
    }),
    {
      name: 'conversation-storage',
      partialize: (state) => ({
        conversations: state.conversations,
        currentConversation: state.currentConversation,
      }),
    }
  )
);
