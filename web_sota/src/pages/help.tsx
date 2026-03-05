import { HelpCircle, Book, MessageSquare, Terminal } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function Help() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">Help & Documentation</h1>
                <p className="text-slate-400">Resources and support for Avatar-MCP.</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center gap-4 text-white">
                        <Book className="h-5 w-5 text-blue-500" />
                        <CardTitle>Getting Started Guide</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 text-sm">
                        Learn how to initialize your first avatar and connect it to the bridge components.
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center gap-4 text-white">
                        <Terminal className="h-5 w-5 text-emerald-500" />
                        <CardTitle>CLI Reference</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 text-sm">
                        Comprehensive documentation for the Command Line Interface and agent tools.
                    </CardContent>
                </Card>
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center gap-4 text-white">
                        <MessageSquare className="h-5 w-5 text-purple-500" />
                        <CardTitle>Community Support</CardTitle>
                    </CardHeader>
                    <CardContent className="text-slate-400 text-sm">
                        Join the discussion or report issues on our GitHub repository.
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
