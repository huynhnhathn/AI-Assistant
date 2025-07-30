import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ChatService, ChatMessage, ChatRequest } from '../services/chat.service';
import { v4 as uuidv4 } from 'uuid';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="chat-container">
      <div class="messages-container" #messagesContainer>
        <div *ngFor="let message of messages" class="message" 
             [ngClass]="message.isUser ? 'user-message' : 'assistant-message'">
          <div [innerHTML]="formatMessage(message.content)"></div>
          <small class="timestamp">{{ message.timestamp | date:'short' }}</small>
        </div>
        
        <div *ngIf="isLoading" class="message assistant-message loading">
          <mat-spinner diameter="20"></mat-spinner>
          <span>AI is thinking...</span>
        </div>
      </div>
      
      <div class="input-container">
        <mat-form-field appearance="outline" style="width: 100%;">
          <mat-label>Type your message...</mat-label>
          <input matInput 
                 [(ngModel)]="currentMessage" 
                 (keydown.enter)="sendMessage()"
                 [disabled]="isLoading"
                 #messageInput>
          <button mat-icon-button 
                  matSuffix 
                  (click)="sendMessage()"
                  [disabled]="!currentMessage.trim() || isLoading">
            <mat-icon>send</mat-icon>
          </button>
        </mat-form-field>
      </div>
    </div>
  `,
  styles: [`
    .chat-container {
      height: calc(100vh - 64px); /* Subtract toolbar height */
      display: flex;
      flex-direction: column;
    }

    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      background-color: #f5f5f5;
    }

    .message {
      margin-bottom: 16px;
      max-width: 70%;
      word-wrap: break-word;
    }

    .user-message {
      margin-left: auto;
      background-color: #3f51b5;
      color: white;
      padding: 12px 16px;
      border-radius: 18px 18px 4px 18px;
    }

    .assistant-message {
      background-color: white;
      padding: 12px 16px;
      border-radius: 18px 18px 18px 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }

    .loading {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #666;
      font-style: italic;
    }

    .input-container {
      padding: 20px;
      background-color: white;
      border-top: 1px solid #e0e0e0;
    }

    .timestamp {
      opacity: 0.7;
      font-size: 0.8em;
      display: block;
      margin-top: 4px;
    }

    .user-message .timestamp {
      color: rgba(255,255,255,0.7);
    }
  `]
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  messages: ChatMessage[] = [];
  currentMessage = '';
  isLoading = false;
  conversationId = uuidv4();

  constructor(
    private chatService: ChatService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    // Add welcome message
    this.messages.push({
      id: uuidv4(),
      content: 'Hello! I\'m your AI assistant. How can I help you today?',
      isUser: false,
      timestamp: new Date()
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  sendMessage() {
    if (!this.currentMessage.trim() || this.isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: uuidv4(),
      content: this.currentMessage,
      isUser: true,
      timestamp: new Date()
    };

    this.messages.push(userMessage);
    
    const request: ChatRequest = {
      message: this.currentMessage,
      conversationId: this.conversationId
    };

    this.currentMessage = '';
    this.isLoading = true;

    this.chatService.sendMessage(request).subscribe({
      next: (response) => {
        const assistantMessage: ChatMessage = {
          id: uuidv4(),
          content: response.response,
          isUser: false,
          timestamp: new Date()
        };
        this.messages.push(assistantMessage);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error sending message:', error);
        this.snackBar.open('Failed to send message. Please try again.', 'Close', {
          duration: 3000
        });
        this.isLoading = false;
      }
    });
  }

  formatMessage(content: string): string {
    // Simple formatting for line breaks
    return content.replace(/\n/g, '<br>');
  }

  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = 
        this.messagesContainer.nativeElement.scrollHeight;
    } catch(err) {
      console.error('Could not scroll to bottom:', err);
    }
  }
}