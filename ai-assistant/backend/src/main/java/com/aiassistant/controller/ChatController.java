package com.aiassistant.controller;

import com.aiassistant.dto.ChatRequest;
import com.aiassistant.dto.ChatResponse;
import com.aiassistant.model.ChatMessage;
import com.aiassistant.service.ChatService;
import com.aiassistant.service.ChatMessageService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/chat")
@CrossOrigin(origins = "http://localhost:4200")
public class ChatController {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatController.class);
    
    private final ChatService chatService;
    private final ChatMessageService chatMessageService;
    
    public ChatController(ChatService chatService, ChatMessageService chatMessageService) {
        this.chatService = chatService;
        this.chatMessageService = chatMessageService;
    }
    
    @PostMapping("/message")
    public ResponseEntity<ChatResponse> sendMessage(@Valid @RequestBody ChatRequest request) {
        logger.info("Received chat message for conversation: {}", request.getConversationId());
        
        try {
            ChatResponse response = chatService.processMessage(request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            logger.error("Error processing chat message", e);
            return ResponseEntity.internalServerError()
                .body(new ChatResponse("Internal server error occurred"));
        }
    }
    
    @GetMapping("/history/{conversationId}")
    public ResponseEntity<List<ChatMessage>> getConversationHistory(@PathVariable String conversationId) {
        logger.info("Retrieving conversation history for: {}", conversationId);
        
        try {
            List<ChatMessage> history = chatMessageService.getConversationHistory(conversationId);
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            logger.error("Error retrieving conversation history", e);
            return ResponseEntity.internalServerError().build();
        }
    }
    
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Chat service is running");
    }
}