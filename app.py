import streamlit as st
import io
import os
from document_processor import DocumentProcessor
from proofreader import Proofreader
from utils import create_download_link, display_diff, get_document_statistics

# Initialize session state
if 'document_processor' not in st.session_state:
    st.session_state.document_processor = None
if 'original_paragraphs' not in st.session_state:
    st.session_state.original_paragraphs = []
if 'corrected_paragraphs' not in st.session_state:
    st.session_state.corrected_paragraphs = []
if 'changes_approved' not in st.session_state:
    st.session_state.changes_approved = {}
if 'edited_paragraphs' not in st.session_state:
    st.session_state.edited_paragraphs = {}
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'upload'

def main():
    st.title("AI-Powered Document Proofreader")
    st.markdown("Upload a Word document (.docx) to get AI-powered proofreading suggestions with highlighted changes.")
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        st.stop()
    
    # Initialize proofreader
    proofreader = Proofreader(api_key)
    
    # Step 1: File Upload
    if st.session_state.current_step == 'upload':
        st.header("📄 Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose a Word document (.docx)",
            type=['docx'],
            help="Upload a .docx file to begin proofreading"
        )
        
        if uploaded_file is not None:
            try:
                # Initialize document processor
                st.session_state.document_processor = DocumentProcessor(uploaded_file)
                
                # Extract paragraphs
                with st.spinner("📖 Reading document..."):
                    st.session_state.original_paragraphs = st.session_state.document_processor.extract_paragraphs()
                
                # Show document statistics
                stats = get_document_statistics(st.session_state.original_paragraphs)
                
                st.success(f"✅ Document loaded successfully!")
                
                # Display document info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Paragraphs", stats['non_empty_paragraphs'])
                with col2:
                    st.metric("Total Words", stats['total_words'])
                with col3:
                    st.metric("Longest Paragraph", f"{stats['longest_paragraph_words']} words")
                
                # Show token usage warning for very long paragraphs
                if stats['longest_paragraph_words'] > 1000:
                    st.warning(f"⚠️ Some paragraphs are very long ({stats['longest_paragraph_words']} words). "
                             f"The system will automatically split them into smaller chunks for processing.")
                
                if st.button("🚀 Start Proofreading", type="primary"):
                    st.session_state.current_step = 'processing'
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
    
    # Step 2: Processing
    elif st.session_state.current_step == 'processing':
        st.header("🔍 AI Proofreading in Progress")
        
        if not st.session_state.processing_complete:
            # Show document statistics
            total_words = sum(len(p.split()) for p in st.session_state.original_paragraphs if p.strip())
            st.info(f"📊 Document contains {len(st.session_state.original_paragraphs)} paragraphs with ~{total_words} words total")
            
            # Process paragraphs
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            corrected_paragraphs = []
            total_paragraphs = len(st.session_state.original_paragraphs)
            
            for i, paragraph in enumerate(st.session_state.original_paragraphs):
                if paragraph.strip():  # Skip empty paragraphs
                    word_count = len(paragraph.split())
                    status_text.text(f"Processing paragraph {i+1} of {total_paragraphs} ({word_count} words)...")
                    
                    try:
                        # Check if paragraph might be split into chunks
                        token_count = proofreader.token_manager.count_tokens(paragraph)
                        if token_count > proofreader.token_manager.max_input_tokens:
                            status_text.text(f"Processing long paragraph {i+1} (splitting into chunks)...")
                        
                        corrected = proofreader.proofread_text(paragraph)
                        corrected_paragraphs.append(corrected)
                    except Exception as e:
                        st.warning(f"⚠️ Error processing paragraph {i+1}: {str(e)}")
                        corrected_paragraphs.append(paragraph)  # Keep original if error
                else:
                    corrected_paragraphs.append(paragraph)  # Keep empty paragraphs as-is
                
                progress_bar.progress((i + 1) / total_paragraphs)
            
            st.session_state.corrected_paragraphs = corrected_paragraphs
            st.session_state.processing_complete = True
            
            # Initialize approval states
            for i in range(len(st.session_state.original_paragraphs)):
                if st.session_state.original_paragraphs[i] != st.session_state.corrected_paragraphs[i]:
                    st.session_state.changes_approved[i] = True  # Default to approved
            
            status_text.text("✅ Processing complete!")
            progress_bar.progress(1.0)
        
        if st.session_state.processing_complete:
            st.success("🎉 Proofreading complete! Review the changes below.")
            
            if st.button("📝 Review Changes", type="primary"):
                st.session_state.current_step = 'review'
                st.rerun()
    
    # Step 3: Review Changes
    elif st.session_state.current_step == 'review':
        st.header("📝 Review and Approve Changes")
        
        changes_found = False
        
        # Display changes for review
        for i, (original, corrected) in enumerate(zip(st.session_state.original_paragraphs, st.session_state.corrected_paragraphs)):
            if original.strip() != corrected.strip() and original.strip():
                changes_found = True
                
                st.subheader(f"Change #{len([j for j in range(i) if st.session_state.original_paragraphs[j] != st.session_state.corrected_paragraphs[j] and st.session_state.original_paragraphs[j].strip()]) + 1}")
                
                # Get the current text (either edited version or original corrected)
                current_text = st.session_state.edited_paragraphs.get(i, corrected)
                
                # Display diff between original and current text
                display_diff(original, current_text)
                
                # Edit section
                with st.expander("✏️ Edit Corrected Text", expanded=False):
                    st.markdown("**Make further edits to the corrected text:**")
                    edited_text = st.text_area(
                        "Edit the corrected paragraph",
                        value=current_text,
                        height=100,
                        key=f"edit_{i}",
                        label_visibility="collapsed"
                    )
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"💾 Save Edit", key=f"save_{i}"):
                            st.session_state.edited_paragraphs[i] = edited_text
                            st.rerun()
                    
                    with col2:
                        if st.button(f"↺ Reset to AI Version", key=f"reset_{i}"):
                            if i in st.session_state.edited_paragraphs:
                                del st.session_state.edited_paragraphs[i]
                            st.rerun()
                
                # Show current version indicator
                if i in st.session_state.edited_paragraphs:
                    st.info("📝 This paragraph has been manually edited")
                
                # Approval checkbox
                approved = st.checkbox(
                    f"✅ Include this paragraph in final document",
                    value=st.session_state.changes_approved.get(i, True),
                    key=f"approve_{i}"
                )
                st.session_state.changes_approved[i] = approved
                
                st.divider()
        
        if not changes_found:
            st.info("🎯 No changes were suggested by the AI. Your document appears to be well-written!")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⬅️ Back to Upload"):
                # Reset session state
                for key in ['document_processor', 'original_paragraphs', 'corrected_paragraphs', 
                           'changes_approved', 'edited_paragraphs', 'processing_complete']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_step = 'upload'
                st.rerun()
        
        with col2:
            if st.button("🔄 Reprocess Document"):
                st.session_state.processing_complete = False
                st.session_state.current_step = 'processing'
                st.rerun()
        
        with col3:
            if st.button("📥 Generate Final Document", type="primary"):
                st.session_state.current_step = 'download'
                st.rerun()
    
    # Step 4: Download
    elif st.session_state.current_step == 'download':
        st.header("📥 Download Corrected Document")
        
        try:
            # Create final paragraphs based on user approval and edits
            final_paragraphs = []
            for i, (original, corrected) in enumerate(zip(st.session_state.original_paragraphs, st.session_state.corrected_paragraphs)):
                if i in st.session_state.changes_approved and st.session_state.changes_approved[i]:
                    # Use edited version if available, otherwise use AI corrected version
                    final_text = st.session_state.edited_paragraphs.get(i, corrected)
                    final_paragraphs.append(final_text)
                else:
                    final_paragraphs.append(original)
            
            # Generate final document
            with st.spinner("📄 Generating final document..."):
                final_doc_bytes = st.session_state.document_processor.create_final_document(final_paragraphs)
            
            # Create download link
            st.success("✅ Final document generated successfully!")
            
            # Show summary
            approved_changes = sum(1 for approved in st.session_state.changes_approved.values() if approved)
            total_changes = len([i for i in range(len(st.session_state.original_paragraphs)) 
                               if st.session_state.original_paragraphs[i] != st.session_state.corrected_paragraphs[i] 
                               and st.session_state.original_paragraphs[i].strip()])
            manual_edits = len(st.session_state.edited_paragraphs)
            
            summary_text = f"📊 Summary: {approved_changes} out of {total_changes} suggested changes were applied"
            if manual_edits > 0:
                summary_text += f", with {manual_edits} manual edits"
            summary_text += "."
            
            st.info(summary_text)
            
            # Download button
            st.download_button(
                label="📥 Download Corrected Document",
                data=final_doc_bytes,
                file_name="corrected_document.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            # Option to start over
            if st.button("🔄 Process Another Document"):
                # Reset session state
                for key in ['document_processor', 'original_paragraphs', 'corrected_paragraphs', 
                           'changes_approved', 'edited_paragraphs', 'processing_complete']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_step = 'upload'
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error generating final document: {str(e)}")
            if st.button("⬅️ Back to Review"):
                st.session_state.current_step = 'review'
                st.rerun()

if __name__ == "__main__":
    main()
