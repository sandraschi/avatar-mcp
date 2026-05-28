import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/common/utils';
import {
    LayoutDashboard,
    Bot,
    Gamepad2,
    Settings,
    ChevronLeft,
    ChevronRight,
    Activity,
    Wrench,
    Video,
    Database,
    Layers,
    Globe,
    Smile,
    Music,
    Clapperboard,
    Boxes,
    Brain,
    Infinity as InfinityIcon,
    HelpCircle,
    Grid,
    ListTodo,
    GitBranch
} from 'lucide-react';

interface SidebarProps {
    collapsed: boolean;
    onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
    const location = useLocation();

    const navItems = [
        { href: '/', label: 'Overview', icon: LayoutDashboard },
        { href: '/control', label: 'Control Center', icon: Gamepad2 },
        { href: '/animation', label: 'Animation', icon: Clapperboard },
        { href: '/emotion', label: 'Emotion', icon: Smile },
        { href: '/audio', label: 'Audio', icon: Music },
        { href: '/registry', label: 'Avatar Registry', icon: Database },
        { href: '/unity', label: 'Unity Bridge', icon: Layers },
        { href: '/vrchat', label: 'VRChat OSC', icon: Globe },
        { href: '/visualizer', label: 'Visualizer', icon: Video },
        { href: '/tools', label: 'Tools Hub', icon: Wrench },
        { href: '/pipeline', label: 'Creative Pipeline', icon: GitBranch },
        { href: '/workflow', label: 'Workflow', icon: ListTodo },
        { href: '/status', label: 'Status', icon: Activity },
        { href: '/apps', label: 'App Hub', icon: Grid },
        { href: '/chat', label: 'AI Command', icon: Bot },
        { href: '/help', label: 'Help', icon: HelpCircle },
        { href: '/intelligence', label: 'Intelligence Hub', icon: Brain },
        { href: '/artifacts', label: 'Artifact Pipeline', icon: Boxes },
        { href: '/loops', label: 'Agent Loops', icon: InfinityIcon },
        { href: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <aside
            className={cn(
                "relative flex flex-col border-r border-slate-800 bg-slate-950/50 backdrop-blur-xl transition-all duration-300 ease-in-out",
                collapsed ? "w-16" : "w-64"
            )}
        >
            <div className="flex h-16 items-center border-b border-slate-800 px-4">
                <div className="flex items-center gap-2 font-semibold text-slate-100">
                    <Activity className="h-6 w-6 text-blue-500" />
                    {!collapsed && <span className="animate-in fade-in duration-300">Avatar-MCP</span>}
                </div>
            </div>

            <nav className="flex-1 space-y-1 p-2 overflow-y-auto">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            to={item.href}
                            className={cn(
                                "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-slate-800 hover:text-white",
                                isActive ? "bg-slate-800 text-white" : "text-slate-400",
                                collapsed ? "justify-center" : "justify-start"
                            )}
                        >
                            <item.icon className={cn("h-5 w-5", !collapsed && "mr-3", isActive && "text-blue-400")} />
                            {!collapsed && <span>{item.label}</span>}

                            {collapsed && (
                                <div className="absolute left-full ml-2 hidden rounded bg-slate-800 px-2 py-1 text-xs text-white group-hover:block z-50 whitespace-nowrap">
                                    {item.label}
                                </div>
                            )}
                        </Link>
                    );
                })}
            </nav>

            <div className="border-t border-slate-800 p-2">
                <button
                    onClick={onToggle}
                    className="flex w-full items-center justify-center rounded-md p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
                >
                    {collapsed ? <ChevronRight className="h-5 w-5" /> : <div className="flex items-center w-full"><ChevronLeft className="h-5 w-5 mr-3" /><span>Collapse</span></div>}
                </button>
            </div>
        </aside>
    );
}
