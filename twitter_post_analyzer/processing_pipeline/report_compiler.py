from typing import Dict, Any, List

async def compile_tweet_report_markdown(
    extracted_data: Dict[str, Any],
    all_image_analysis_results: List[Dict[str, Any]],
    all_video_analysis_results: List[Dict[str, Any]],
    all_link_analysis_results: List[Dict[str, Any]]
) -> str:
    """
    Compiles a Markdown report from extracted tweet data and analysis results.
    """
    report_parts = []

    # Determine report type
    is_full_analysis = (
        len(all_image_analysis_results) > 0 or
        len(all_video_analysis_results) > 0 or
        len(all_link_analysis_results) > 0
    )
    report_type = "Full Analysis Report" if is_full_analysis else "Text-Only Summary"

    report_parts.append(f"# Tweet Analysis Report (ID: {extracted_data.get('analysis_id', 'N/A')})\n")
    report_parts.append(f"## Report Type: {report_type}\n")

    # Iterate through each post
    for post_data in extracted_data.get("all_posts_structured", []):
        post_id = post_data.get("post_id", "N/A")
        author = post_data.get("author", "Unknown Author")
        created_at = post_data.get("created_at", "N/A")
        text = post_data.get("text", "")
        parent_post_id = post_data.get("parent_post_id")
        quoted_post_id = post_data.get("quoted_post_id")

        report_parts.append(f"---")
        report_parts.append(f"### Post ID: {post_id}")
        report_parts.append(f"**Author:** {author}")
        report_parts.append(f"**Created At:** {created_at}")
        if parent_post_id:
            report_parts.append(f"**In Reply To:** {parent_post_id}")
        if quoted_post_id:
            report_parts.append(f"**Quoted Post:** {quoted_post_id}")
        report_parts.append(f"\n**Text:**\n```\n{text}\n```\n")

        # Add media analysis results for this post
        post_media_analysis = [
            res for res in all_image_analysis_results if res.get("post_id") == post_id
        ] + [
            res for res in all_video_analysis_results if res.get("post_id") == post_id
        ]
        if post_media_analysis:
            report_parts.append("#### Media Analysis:")
            for media_res in post_media_analysis:
                media_type = media_res.get("type", "unknown")
                local_path = media_res.get("local_path", "N/A")
                original_url = media_res.get("original_url", "N/A")
                analysis_desc = media_res.get("analysis", {}).get("description", "No description available.")
                analysis_error = media_res.get("analysis", {}).get("error")

                report_parts.append(f"- **Type:** {media_type.capitalize()}")
                report_parts.append(f"  - **Local Path:** `{local_path}`")
                report_parts.append(f"  - **Original URL:** {original_url}")
                if analysis_error:
                    report_parts.append(f"  - **Analysis Error:** {analysis_error}")
                else:
                    report_parts.append(f"  - **Description:** {analysis_desc}")
            report_parts.append("\n")

        # Add link analysis results for this post
        post_link_analysis = [
            res for res in all_link_analysis_results if res.get("post_id") == post_id
        ]
        if post_link_analysis:
            report_parts.append("#### Link Analysis:")
            for link_res in post_link_analysis:
                url = link_res.get("url", "N/A")
                summary = link_res.get("analysis", {}).get("summary", "No summary available.")
                search_results = link_res.get("analysis", {}).get("search_results", [])
                analysis_error = link_res.get("analysis", {}).get("error")

                report_parts.append(f"- **URL:** {url}")
                if analysis_error:
                    report_parts.append(f"  - **Analysis Error:** {analysis_error}")
                else:
                    report_parts.append(f"  - **Summary:** {summary}")
                    if search_results:
                        report_parts.append("  - **Top Search Results:**")
                        for sr in search_results[:3]: # Limit to top 3 results
                            report_parts.append(f"    - [{sr.get('title', 'N/A')}]({sr.get('link', '#')})")
                            report_parts.append(f"      > {sr.get('snippet', 'No snippet.')}")
            report_parts.append("\n")

    return "\n".join(report_parts)