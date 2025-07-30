package com.aiassistant.dto;

import java.util.List;

public class ChatResponse {
    
    private String response;
    private String conversationId;
    private List<String> sources;
    private boolean success;
    private String error;

    public ChatResponse() {}

    public ChatResponse(String response, String conversationId) {
        this.response = response;
        this.conversationId = conversationId;
        this.success = true;
    }

    public ChatResponse(String error) {
        this.error = error;
        this.success = false;
    }

    public String getResponse() {
        return response;
    }

    public void setResponse(String response) {
        this.response = response;
    }

    public String getConversationId() {
        return conversationId;
    }

    public void setConversationId(String conversationId) {
        this.conversationId = conversationId;
    }

    public List<String> getSources() {
        return sources;
    }

    public void setSources(List<String> sources) {
        this.sources = sources;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}