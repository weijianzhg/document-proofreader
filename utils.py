import streamlit as st
import difflib
import html
from typing import List

def create_download_link(file_bytes, filename, link_text):
    """Create a download link for file bytes"""
    import base64
    b64 = base64.b64encode(file_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def create_word_level_diff(original, corrected):
    """Create highlighted HTML versions showing word-level changes"""
    original_words = original.split()
    corrected_words = corrected.split()
    
    differ = difflib.SequenceMatcher(None, original_words, corrected_words)
    
    original_html = []
    corrected_html = []
    
    for tag, i1, i2, j1, j2 in differ.get_opcodes():
        if tag == 'equal':
            # Words that are the same
            for word in original_words[i1:i2]:
                original_html.append(html.escape(word))
            for word in corrected_words[j1:j2]:
                corrected_html.append(html.escape(word))
        elif tag == 'delete':
            # Words removed from original
            for word in original_words[i1:i2]:
                original_html.append(f'<span style="background-color: #ffebee; color: #c62828; text-decoration: line-through; padding: 2px 4px; border-radius: 3px; margin: 1px;">{html.escape(word)}</span>')
        elif tag == 'insert':
            # Words added to corrected
            for word in corrected_words[j1:j2]:
                corrected_html.append(f'<span style="background-color: #e8f5e8; color: #2e7d32; font-weight: bold; padding: 2px 4px; border-radius: 3px; margin: 1px;">{html.escape(word)}</span>')
        elif tag == 'replace':
            # Words changed
            for word in original_words[i1:i2]:
                original_html.append(f'<span style="background-color: #fff3e0; color: #f57c00; text-decoration: line-through; padding: 2px 4px; border-radius: 3px; margin: 1px;">{html.escape(word)}</span>')
            for word in corrected_words[j1:j2]:
                corrected_html.append(f'<span style="background-color: #e3f2fd; color: #1976d2; font-weight: bold; padding: 2px 4px; border-radius: 3px; margin: 1px;">{html.escape(word)}</span>')
    
    return ' '.join(original_html), ' '.join(corrected_html)

def get_word_diff(original, corrected):
    """Get word-level differences between two texts"""
    original_words = original.split()
    corrected_words = corrected.split()
    
    differ = difflib.SequenceMatcher(None, original_words, corrected_words)
    
    changes = []
    for tag, i1, i2, j1, j2 in differ.get_opcodes():
        if tag == 'delete':
            changes.append({
                'type': 'delete',
                'text': ' '.join(original_words[i1:i2])
            })
        elif tag == 'insert':
            changes.append({
                'type': 'insert',
                'text': ' '.join(corrected_words[j1:j2])
            })
        elif tag == 'replace':
            changes.append({
                'type': 'replace',
                'original': ' '.join(original_words[i1:i2]),
                'corrected': ' '.join(corrected_words[j1:j2])
            })
    
    return changes

def get_change_summary(original, corrected):
    """Get a summary of changes made"""
    return get_word_diff(original, corrected)

def display_diff(original_text, corrected_text):
    """Display a visual diff between original and corrected text"""
    if original_text.strip() == corrected_text.strip():
        st.info("No changes suggested for this paragraph.")
        return
    
    # Create highlighted versions
    original_highlighted, corrected_highlighted = create_word_level_diff(original_text, corrected_text)
    
    # Create a side-by-side comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Original:**")
        st.markdown(f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; min-height: 150px; border: 1px solid #dee2e6; font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6;">{original_highlighted}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Corrected:**")
        st.markdown(f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; min-height: 150px; border: 1px solid #dee2e6; font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6;">{corrected_highlighted}</div>', unsafe_allow_html=True)
    
    # Show detailed changes summary
    changes = get_change_summary(original_text, corrected_text)
    if changes:
        with st.expander("📝 Summary of Changes"):
            for change in changes:
                if change['type'] == 'replace':
                    st.markdown(f"• **Changed:** '{change['original']}' → '{change['corrected']}'")
                elif change['type'] == 'delete':
                    st.markdown(f"• **Removed:** '{change['text']}'")
                elif change['type'] == 'insert':
                    st.markdown(f"• **Added:** '{change['text']}'")
    
    # Show line-by-line diff for detailed analysis
    with st.expander("🔍 Line-by-Line Comparison"):
        diff_html = create_html_diff(original_text, corrected_text)
        st.markdown(diff_html, unsafe_allow_html=True)

def create_html_diff(original, corrected):
    """Create HTML diff highlighting changes"""
    differ = difflib.unified_diff(
        original.splitlines(keepends=True),
        corrected.splitlines(keepends=True),
        fromfile='Original',
        tofile='Corrected',
        lineterm=''
    )
    
    diff_lines = list(differ)
    if not diff_lines:
        return "<p>No changes detected.</p>"
    
    html_parts = []
    html_parts.append("<div style='font-family: monospace; font-size: 12px; line-height: 1.4;'>")
    
    for line in diff_lines:
        if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
            html_parts.append(f"<div style='color: #666; font-weight: bold;'>{html.escape(line.rstrip())}</div>")
        elif line.startswith('-'):
            html_parts.append(f"<div style='background-color: #ffecec; color: #d63031; padding: 2px;'>- {html.escape(line[1:].rstrip())}</div>")
        elif line.startswith('+'):
            html_parts.append(f"<div style='background-color: #e8f5e8; color: #00b894; padding: 2px;'>+ {html.escape(line[1:].rstrip())}</div>")
        else:
            html_parts.append(f"<div style='padding: 2px;'>  {html.escape(line.rstrip())}</div>")
    
    html_parts.append("</div>")
    return ''.join(html_parts)

def highlight_changes(original, corrected):
    """Create highlighted version showing changes"""
    if original == corrected:
        return corrected
    
    # Simple highlighting for now - could be enhanced with more sophisticated diff
    return f"~~{original}~~ → **{corrected}**"

def validate_document_format(file):
    """Validate that the uploaded file is a valid .docx document"""
    if not file.name.lower().endswith('.docx'):
        return False, "File must be a .docx document"
    
    try:
        # Try to read the file as a docx
        from docx import Document
        Document(file)
        return True, "Valid document"
    except Exception as e:
        return False, f"Invalid .docx file: {str(e)}"

def count_words(text):
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())

def estimate_processing_time(word_count):
    """Estimate processing time based on word count"""
    # Rough estimate: ~100 words per API call, ~2 seconds per call
    estimated_calls = max(1, word_count // 100)
    estimated_seconds = estimated_calls * 2
    
    if estimated_seconds < 60:
        return f"~{estimated_seconds} seconds"
    else:
        minutes = estimated_seconds // 60
        return f"~{minutes} minute(s)"

def get_document_statistics(paragraphs):
    """Get comprehensive statistics about the document"""
    total_paragraphs = len(paragraphs)
    non_empty_paragraphs = len([p for p in paragraphs if p.strip()])
    total_words = sum(len(p.split()) for p in paragraphs if p.strip())
    total_chars = sum(len(p) for p in paragraphs if p.strip())
    
    # Find longest paragraph
    longest_paragraph_words = 0
    longest_paragraph_chars = 0
    
    for p in paragraphs:
        if p.strip():
            words = len(p.split())
            chars = len(p)
            if words > longest_paragraph_words:
                longest_paragraph_words = words
            if chars > longest_paragraph_chars:
                longest_paragraph_chars = chars
    
    return {
        'total_paragraphs': total_paragraphs,
        'non_empty_paragraphs': non_empty_paragraphs,
        'total_words': total_words,
        'total_chars': total_chars,
        'longest_paragraph_words': longest_paragraph_words,
        'longest_paragraph_chars': longest_paragraph_chars,
        'avg_words_per_paragraph': total_words / max(1, non_empty_paragraphs)
    }