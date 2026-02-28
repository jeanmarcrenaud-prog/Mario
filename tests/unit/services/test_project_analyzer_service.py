from src.services.project_analyzer_service import SimulatedLLMAdapter, ProjectAnalyzerService


def test_project_analyzer_service_basic(tmp_path):
    # Setup: create a small project structure
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# Test project")
    (tmp_path / "requirements.txt").write_text("requests\n")

    # Use simulated LLM adapter
    llm_adapter = SimulatedLLMAdapter()
    service = ProjectAnalyzerService(llm_adapter=llm_adapter)

    report = service.analyze_project(str(tmp_path), depth=1)
    # Basic sanity checks
    assert report.get("project_name") == tmp_path.name
    assert report.get("ai_analysis") is not None
    assert "full_analysis" in report["ai_analysis"]
    assert isinstance(report["ai_analysis"]["full_analysis"], str)
    # Ensure some summary content
    assert "📊 Résumé" in report.get("summary", "")
