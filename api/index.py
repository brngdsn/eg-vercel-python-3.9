from http.server import BaseHTTPRequestHandler
import json
import sys
import platform
import os

import asyncio
import traceback
from readmeai.config.settings import (
    AppConfig,
    AppConfigModel,
    ConfigHelper,
    GitConfig,
    load_config,
    load_config_helper,
)
from readmeai.core import logger, model, preprocess
from readmeai.markdown import headers, tables, tree
from readmeai.services import version_control as vcs

logger = logger.Logger(__name__)

def get_response_content(readme_content):
    return {
            'readme': readme_content,
            'message': '(P)ython(API)',
            'readmeai_version': readmeai.__version__,
            'readmeai_path': list(readmeai.__path__),
            'version': sys.version,
            'version_info': {
                'major': sys.version_info.major,
                'minor': sys.version_info.minor,
                'micro': sys.version_info.micro,
                'releaselevel': sys.version_info.releaselevel,
                'serial': sys.version_info.serial
            },
            'platform': sys.platform,
            'executable': sys.executable,
            'prefix': sys.prefix,
            'base_prefix': sys.base_prefix,
            'byteorder': sys.byteorder,
            'maxsize': sys.maxsize,
            'maxunicode': sys.maxunicode,
            'path': sys.path,
            'argv': sys.argv,
            'flags': {
                'debug': sys.flags.debug,
                'inspect': sys.flags.inspect,
                'interactive': sys.flags.interactive,
                'optimize': sys.flags.optimize,
                'dont_write_bytecode': sys.flags.dont_write_bytecode,
                'no_user_site': sys.flags.no_user_site,
                'no_site': sys.flags.no_site,
                'ignore_environment': sys.flags.ignore_environment,
                'verbose': sys.flags.verbose,
                'quiet': sys.flags.quiet,
                'isolated': sys.flags.isolated
            },
            'recursion_limit': sys.getrecursionlimit(),
            'os': {
                'name': os.name,
                'cpu_count': os.cpu_count(),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A'
            },
            'platform_info': {
                'system': platform.system(),
                'node': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }
        }

async def readme_agent(conf: AppConfig, conf_helper: ConfigHelper) -> None:
    """Orchestrates the README file generation process."""
    logger.info("README-AI is now executing.")
    logger.info(f"User Repository: {conf.git.repository}")
    logger.info(f"Output File: {conf.paths.output}")
    logger.info(f"Model Engine:  {conf.api.model}")

    name = conf.git.name
    placeholder = conf.md.default
    repository = conf.git.repository

    llm = model.OpenAIHandler(conf)

    try:
        temp_dir = vcs.clone_repo_to_temp_dir(repository)
        tree_generator = tree.TreeGenerator(
            conf_helper,
            temp_dir,
            repository,
            project_name="readmeai",
            max_depth=3,
        )
        tree_str = tree_generator.generate_and_format_tree()
        conf.md.tree = conf.md.tree.format(tree_str)
        logger.info(f"Repository tree: {conf.md.tree}")

        parser = preprocess.RepositoryParser(conf, conf_helper)
        dependencies, files = parser.get_dependencies(temp_dir)
        logger.info(f"Dependencies: {dependencies}")
        logger.info(f"Files: {files}")

        # Generate codebase file summaries and README.md text via LLMs.
        if conf.cli.offline is False:
            code_summary = await llm.code_to_text(
                conf_helper.ignore_files,
                files,
                conf.prompts.code_summary,
            )
            logger.info(f"Code summaries returned:\n{code_summary[:5]}")
            prompts = [
                conf.prompts.slogan.format(conf.git.name),
                conf.prompts.overview.format(repository, code_summary),
                conf.prompts.features.format(repository, tree),
            ]
            slogan, overview, features = await llm.chat_to_text(prompts)

        else:
            conf.md.tables = tables.build_recursive_tables(
                repository, temp_dir, placeholder
            )
            code_summary = placeholder
            slogan, overview, features = (
                conf.md.default,
                conf.md.default,
                conf.md.default,
            )

        # Generate README.md file.
        conf.prompts.slogan = slogan
        conf.md.header = conf.md.header.format(name.upper(), slogan)
        conf.md.intro = conf.md.intro.format(overview, features)
        headers.build_readme_md(conf, conf_helper, dependencies, code_summary)

    except Exception as excinfo:
        logger.error(
            f"Exception: {excinfo}\nStacktrace: {traceback.format_exc()}"
        )
    finally:
        await llm.close()

    logger.info("README-AI execution complete.")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        readme_content = 'n/a'

        conf = load_config()
        conf_model = AppConfigModel(app=conf)
        conf_helper = load_config_helper(conf_model)
        conf.api.model = 'gpt-4o-mini'
        conf.cli.badges = True
        conf.cli.emojis = True
        conf.api.model = 'gpt-4o-mini'
        conf.cli.offline = True
        conf.paths.output = 'README.md'
        conf.api.temperature = 0.7
        conf.git = GitConfig(repository='https://github.com/brngdsn/unmd', name=None)
        conf.git.name = vcs.get_user_repository_name('https://github.com/brngdsn/unmd')[1]
        logger.info(f"Configuration: {conf.git}")
        asyncio.run(readme_agent(conf, conf_helper))

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        if os.path.exists("README.md"):
            with open("README.md", "r", encoding="utf-8") as f:
                readme_content = f.read()
        else:
            readme_content = "README file not found."

        response_content = get_response_content(readme_content)

        self.wfile.write(json.dumps(response_content).encode())
