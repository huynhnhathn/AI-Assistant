package com.aiassistant.service;

import com.aiassistant.model.ChatMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.stereotype.Service;

import java.util.List;

@Repository
interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {
    List<ChatMessage> findByConversationIdOrderByTimestampAsc(String conversationId);
}

@Service
public class ChatMessageService {
    
    private final ChatMessageRepository repository;
    
    public ChatMessageService(ChatMessageRepository repository) {
        this.repository = repository;
    }
    
    public ChatMessage saveMessage(ChatMessage message) {
        return repository.save(message);
    }
    
    public List<ChatMessage> getConversationHistory(String conversationId) {
        return repository.findByConversationIdOrderByTimestampAsc(conversationId);
    }
}