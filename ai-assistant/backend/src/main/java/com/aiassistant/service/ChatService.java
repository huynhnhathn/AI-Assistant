package com.aiassistant.service;

import com.aiassistant.dto.ChatRequest;
import com.aiassistant.dto.ChatResponse;
import com.aiassistant.model.ChatMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.ResourceAccessException;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

@Service
public class ChatService {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatService.class);
    
    @Value("${langchain.service.url}")
    private String langchainServiceUrl;
    
    @Value("${langchain.service.timeout}")
    private int timeout;
    
    private final RestTemplate restTemplate;
    private final ChatMessageService chatMessageService;
    
    public ChatService(ChatMessageService chatMessageService) {
        this.chatMessageService = chatMessageService;
        this.restTemplate = new RestTemplate();
        // Configure timeout
        this.restTemplate.setRequestFactory(new org.springframework.http.client.SimpleClientHttpRequestFactory());
    }

    public ChatResponse processMessage(ChatRequest request) {
        try {
            logger.info("Processing message for conversation: {}", request.getConversationId());
            
            // Save user message
            ChatMessage userMessage = new ChatMessage(
                request.getConversationId(), 
                request.getMessage(), 
                true
            );
            chatMessageService.saveMessage(userMessage);
            
            // Prepare request to LangChain service
            Map<String, Object> langchainRequest = new HashMap<>();
            langchainRequest.put("query", request.getMessage());
            langchainRequest.put("conversation_id", request.getConversationId());
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(langchainRequest, headers);
            
            // Call LangChain service
            String url = langchainServiceUrl + "/chat";
            logger.debug("Calling LangChain service at: {}", url);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> responseBody = response.getBody();
                String aiResponse = (String) responseBody.get("response");
                
                // Save AI response
                ChatMessage aiMessage = new ChatMessage(
                    request.getConversationId(),
                    aiResponse,
                    false
                );
                chatMessageService.saveMessage(aiMessage);
                
                ChatResponse chatResponse = new ChatResponse(aiResponse, request.getConversationId());
                
                // Add sources if available
                if (responseBody.containsKey("sources")) {
                    chatResponse.setSources((java.util.List<String>) responseBody.get("sources"));
                }
                
                logger.info("Successfully processed message for conversation: {}", request.getConversationId());
                return chatResponse;
            } else {
                logger.error("LangChain service returned error status: {}", response.getStatusCode());
                return new ChatResponse("Sorry, I'm having trouble processing your request right now.");
            }
            
        } catch (ResourceAccessException e) {
            logger.error("Timeout or connection error calling LangChain service", e);
            return new ChatResponse("Sorry, the AI service is currently unavailable. Please try again later.");
        } catch (Exception e) {
            logger.error("Error processing chat message", e);
            return new ChatResponse("Sorry, I encountered an error processing your request.");
        }
    }
}