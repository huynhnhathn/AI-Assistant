#!/usr/bin/env python3
"""
RAG Application - Main CLI Interface
A Retrieval-Augmented Generation application using LangChain, Qdrant, and OpenAI
"""

import click
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from typing import Optional

from src.rag_app.core.config import config
from src.rag_app.core.rag_chain import RAGChain
from src.rag_app.utils.logging_config import setup_logging

console = Console()

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', help='Log file path')
def cli(verbose: bool, log_file: Optional[str]):
    """RAG Application CLI - Retrieval-Augmented Generation with LangChain, Qdrant, and OpenAI"""
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level, log_file=log_file)
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        console.print(f"[red]Configuration Error: {e}[/red]")
        console.print("[yellow]Please check your .env file or environment variables[/yellow]")
        raise click.Abort()

@cli.command()
@click.argument('source', type=str)
@click.option('--type', 'source_type', 
              type=click.Choice(['file', 'directory', 'url']), 
              default='file',
              help='Type of source to process')
@click.option('--pattern', default='**/*', help='Glob pattern for directory processing')
def add_documents(source: str, source_type: str, pattern: str):
    """Add documents to the RAG system"""
    
    console.print(f"[blue]Adding documents from {source_type}: {source}[/blue]")
    
    try:
        # Initialize RAG chain
        with console.status("[bold green]Initializing RAG system..."):
            rag = RAGChain()
        
        # Add documents
        with console.status("[bold green]Processing and adding documents..."):
            result = rag.add_documents_from_source(
                source=source,
                source_type=source_type,
                glob_pattern=pattern
            )
        
        if result["status"] == "success":
            console.print(f"[green]✓ {result['message']}[/green]")
            
            # Display statistics
            stats = result.get("stats", {})
            if stats:
                table = Table(title="Document Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Total Documents", str(stats.get("total_documents", 0)))
                table.add_row("Total Characters", str(stats.get("total_characters", 0)))
                table.add_row("Average Chunk Size", f"{stats.get('average_chunk_size', 0):.0f}")
                table.add_row("Unique Sources", str(stats.get("unique_sources", 0)))
                
                console.print(table)
        else:
            console.print(f"[red]✗ Error: {result['message']}[/red]")
            
    except Exception as e:
        console.print(f"[red]✗ Failed to add documents: {e}[/red]")
        raise click.Abort()

@cli.command()
@click.argument('question', type=str)
@click.option('--sources', '-k', default=4, help='Number of source documents to retrieve')
@click.option('--threshold', type=float, help='Similarity score threshold')
@click.option('--memory/--no-memory', default=False, help='Use conversation memory')
def query(question: str, sources: int, threshold: Optional[float], memory: bool):
    """Query the RAG system"""
    
    try:
        # Initialize RAG chain
        with console.status("[bold green]Initializing RAG system..."):
            rag = RAGChain()
        
        # Perform query
        with console.status("[bold green]Searching and generating answer..."):
            result = rag.query(
                question=question,
                k=sources,
                score_threshold=threshold,
                use_memory=memory
            )
        
        if result["status"] == "success":
            # Display answer
            console.print(Panel(
                Markdown(result["answer"]),
                title="[bold green]Answer[/bold green]",
                border_style="green"
            ))
            
            # Display sources
            if result.get("sources"):
                console.print("\n[bold blue]Sources:[/bold blue]")
                for i, source in enumerate(result["sources"], 1):
                    console.print(f"\n[cyan]{i}. {source['file_name']}[/cyan]")
                    console.print(f"   Source: {source['source']}")
                    console.print(f"   Preview: {source['content_preview']}")
        else:
            console.print(f"[red]✗ Error: {result['message']}[/red]")
            
    except Exception as e:
        console.print(f"[red]✗ Query failed: {e}[/red]")
        raise click.Abort()

@cli.command()
def interactive():
    """Start interactive chat mode"""
    
    try:
        # Initialize RAG chain
        with console.status("[bold green]Initializing RAG system..."):
            rag = RAGChain()
        
        console.print("[bold green]RAG Interactive Chat Mode[/bold green]")
        console.print("[yellow]Type 'quit', 'exit', or 'bye' to end the session[/yellow]")
        console.print("[yellow]Type 'clear' to clear conversation memory[/yellow]")
        console.print("[yellow]Type 'status' to check system status[/yellow]\n")
        
        while True:
            try:
                question = console.input("[bold blue]You: [/bold blue]")
                
                if question.lower() in ['quit', 'exit', 'bye']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if question.lower() == 'clear':
                    rag.clear_memory()
                    console.print("[green]✓ Conversation memory cleared[/green]")
                    continue
                
                if question.lower() == 'status':
                    status = rag.get_system_status()
                    table = Table(title="System Status")
                    table.add_column("Component", style="cyan")
                    table.add_column("Status", style="green")
                    
                    table.add_row("Vector Store", "✓ Healthy" if status.get("vector_store_healthy") else "✗ Unhealthy")
                    table.add_row("LLM Model", status.get("llm_model", "Unknown"))
                    table.add_row("Embedding Model", status.get("embedding_model", "Unknown"))
                    table.add_row("Memory Messages", str(status.get("memory_messages", 0)))
                    
                    console.print(table)
                    continue
                
                if not question.strip():
                    continue
                
                # Process query
                with console.status("[bold green]Thinking..."):
                    result = rag.query(question, use_memory=True)
                
                if result["status"] == "success":
                    console.print(f"[bold green]Assistant:[/bold green] {result['answer']}\n")
                else:
                    console.print(f"[red]Error: {result['message']}[/red]\n")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except EOFError:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
                
    except Exception as e:
        console.print(f"[red]✗ Interactive mode failed: {e}[/red]")
        raise click.Abort()

@cli.command()
def status():
    """Check system status and health"""
    
    try:
        # Initialize RAG chain
        with console.status("[bold green]Checking system status..."):
            rag = RAGChain()
            status = rag.get_system_status()
        
        # Create status table
        table = Table(title="RAG System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # Vector store status
        vs_status = "✓ Healthy" if status.get("vector_store_healthy") else "✗ Unhealthy"
        table.add_row("Vector Store", vs_status, "Qdrant connection")
        
        # Models
        table.add_row("LLM Model", status.get("llm_model", "Unknown"), "OpenAI Chat Model")
        table.add_row("Embedding Model", status.get("embedding_model", "Unknown"), "OpenAI Embeddings")
        
        # Collection info
        collection_info = status.get("collection_info", {})
        if isinstance(collection_info, dict) and "error" not in collection_info:
            table.add_row("Documents", str(collection_info.get("points_count", 0)), "Total document chunks")
            table.add_row("Vectors", str(collection_info.get("vectors_count", 0)), "Indexed vectors")
        
        # Memory
        table.add_row("Memory", str(status.get("memory_messages", 0)), "Conversation messages")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗ Status check failed: {e}[/red]")
        raise click.Abort()

@cli.command()
def info():
    """Display application information"""
    
    info_text = """
    # RAG Application
    
    A Retrieval-Augmented Generation application built with:
    - **LangChain**: Framework for LLM applications
    - **Qdrant**: Vector database for similarity search
    - **OpenAI**: Language models and embeddings
    
    ## Features
    - Document processing (PDF, DOCX, TXT, MD, etc.)
    - Vector similarity search
    - Conversational memory
    - Interactive chat mode
    - Batch processing
    
    ## Configuration
    - Configuration file: `.env`
    - Vector database: Qdrant
    - Default collection: `rag_documents`
    """
    
    console.print(Panel(
        Markdown(info_text),
        title="[bold blue]Application Information[/bold blue]",
        border_style="blue"
    ))

if __name__ == "__main__":
    cli()