PID: 2610804 starting at Sun 08 Mar 2026 11:41:10 PM CDT
goal: enforce Data() hierarchy — all persistence goes through put_data/get_data
read shared/data.py, server/data.py, all client files, pm.py, queue_worker.py, benchmark_service.py, api_key_manager.py
fix client state: claude.py, gemini.py, chatgpt.py, dmrbot.py — use put_data/get_data instead of direct file writes
user insight: non-hierarchy scripts should instantiate Service(None) to get full hierarchy incl Platform for paths
fixing: claude.py, gemini.py, chatgpt.py, dmrbot.py — remove state_file, use put_data/get_data
fixing: benchmark_service.py — use put_data/get_data for benchmarks metadata
fixing: api_key_manager.py — subclass Service()
fixing: pm.py — instantiate Service(None) for state/logging
fixing: queue_worker.py — instantiate Service(None) for agent tracking
adding: csc-ctl data command — list/get/set/del keys in any Data store
fix api_key_manager.py: subclass Service() instead of direct file I/O
fix pm.py: instantiate Service(None) for state and logging
fix queue_worker.py: use Service(None) for write_agent_data/clear_agent_data
add csc-ctl data command and bin/data helper script echo commit all data hierarchy fixes python3 bin/refresh-maps --quick
done — all data hierarchy fixes committed and pushed
