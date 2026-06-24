> ## Documentation Index
> Fetch the complete documentation index at: https://docs.replit.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Use Agent Skills

> Give Agent specialized knowledge with Agent Skills — attach one to a message, install one in your project, or start a project from one.

export const AiPrompt = ({children}) => {
  return <CodeBlock className="relative block font-sans whitespace-pre-wrap break-words">
      <div className="pr-7">
        {children}
      </div>
    </CodeBlock>;
};

Skills teach Agent new capabilities — preferred patterns, library specifics, design system rules, or solutions to problems you've already solved. Attach one to a message, install one in your project, or pick one as a starting point for a new project.

## Use a skill in chat

The fastest way to try skills is to attach one to a single message — no installation needed.

<Frame>
  <img src="https://mintcdn.com/replit/NqvyWjOnebeS7HrG/images/replitai/agent-skills-picker.png?fit=max&auto=format&n=NqvyWjOnebeS7HrG&q=85&s=9d8a34ad8c89793dac6e51cb86073ce2" alt="Skill picker opened from the + button next to the chat input, showing the Skills list with Ad Creative, AI Recruiter, AI SDR, and AI Secretary" width="723" height="529" data-path="images/replitai/agent-skills-picker.png" />
</Frame>

<Steps>
  <Step title="Open the skill picker">
    Click the **+** button next to the chat input and select **Use a skill**.
  </Step>

  <Step title="Browse and select a skill">
    Browse skills by category — Business & finance, Creative, Research & analysis, and more. Select one or more skills to attach to your message.
  </Step>

  <Step title="Send your message">
    Type your request and send. Agent uses the selected skills for that message only. A skill chip appears on your message so you can see which skills are active.
  </Step>
</Steps>

For example, attach **Stock Analyzer** and ask Agent to build an equity research report, or attach **Deep Research** to have Agent investigate a topic with structured findings.

<Tip>
  Skills attached in chat don't install anything in your project. They're available instantly in every project.
</Tip>

## Start a project with a skill

When you create a new project, you can pick a pre-vetted skill as the starting point. Agent uses the skill's instructions to scaffold the project.

<Steps>
  <Step title="Open the starting point picker">
    On the new-project screen, click **+** and select **Use a skill**.
  </Step>

  <Step title="Pick a skill">
    Browse curated skills like **AI SDR**, **SEO Auditor**, **Ad Creative**, or **Programmatic SEO**. Select the one that matches the kind of app you want to build.
  </Step>

  <Step title="Describe your app">
    Tell Agent what you want. Agent builds the project with the skill's patterns and conventions applied from the start.
  </Step>
</Steps>

## Install a skill in your project

When you want Agent to apply a skill consistently across every conversation in a project, install it. Installed skills live in your project's `/.agents/skills` directory and persist across chat sessions.

### Install from the Skills pane

Open the **Skills pane** in the Project Editor and select the **Discover** tab to search community-contributed skills. Find one you want, click **Install**, and it's added to your project automatically.

<Frame>
  <img src="https://mintcdn.com/replit/gerX13Tz1112Sdux/images/replitai/agent-skills-discover.png?fit=max&auto=format&n=gerX13Tz1112Sdux&q=85&s=25ed47eb8abea795f960b132c3e44b61" alt="Discover skills tab showing searchable community-contributed skills with install buttons" width="2542" height="1850" data-path="images/replitai/agent-skills-discover.png" />
</Frame>

For example, when building a portfolio site with advanced animations, you might install:

* **GSAP React** — teaches Agent scroll-triggered animations, text reveals, and SVG path drawing
* **Tailwind design system** — gives Agent knowledge of Tailwind CSS patterns for typography, spacing, and view transitions
* **Find skills** — teaches Agent how to discover and install new skills on your behalf

<Tip>
  You can also install skills via the [npx skills CLI](https://github.com/vercel-labs/skills):

  ```bash theme={null}
  npx skills <skill> -a replit
  ```
</Tip>

### Create a skill from a conversation

The most natural way to create a skill is through conversation with Agent. After solving a problem together or researching a new library, ask Agent to capture what it learned:

<AiPrompt>
  Research best practices for GSAP React integration and create a skill for this project.
</AiPrompt>

Agent uses the full conversation context to write a detailed skill file. This works particularly well after debugging sessions where you've built up shared understanding of a problem.

### Write a custom skill

For advanced use cases, write skills directly following the [Agent Skills specification](https://agentskills.io/specification). Toggle **Show Hidden Files** in the file sidebar, open `/.agents/skills/`, and create a new Markdown file. This gives you complete control over what Agent knows and how it behaves.

## Next steps

<CardGroup cols={2}>
  <Card title="Agent skills (concepts)" icon="puzzle-piece" href="/learn/agent-skills">
    Learn when to use skills, proactive vs reactive patterns, and how skills compare to MCP servers.
  </Card>

  <Card title="Agent Skills reference" icon="book" href="/references/agent/skills">
    Technical details on skill structure, management, and how skills work under the hood.
  </Card>

  <Card title="Browse community skills" icon="arrow-up-right-from-square" href="https://skills.sh">
    Find skills built by the community at skills.sh.
  </Card>

  <Card title="Agent Skills specification" icon="file-lines" href="https://agentskills.io/specification">
    Read the open standard so you can write skills that work across any agent.
  </Card>
</CardGroup>

