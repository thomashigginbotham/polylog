import React, { useState } from 'react';
import { useWebSocket } from '../contexts/WebSocketContext';

export default function ChatPage() {
  const { messages, sendMessage, connectionStatus, isConnected } = useWebSocket();
  const [newMessage, setNewMessage] = useState('');

  const handleSendMessage = () => {
    if (newMessage.trim() !== '' && isConnected) {
      sendMessage(newMessage);
      setNewMessage('');
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-500';
      case 'connecting': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return '🟢 Connected';
      case 'connecting': return '🟡 Connecting...';
      case 'error': return '🔴 Connection Error';
      default: return '⚪ Disconnected';
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
        <div className="p-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Polylog</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Many voices, one conversation</p>
        </div>
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Connection Status</h3>
          <div className={`text-sm font-medium ${getConnectionStatusColor()}`}>
            {getConnectionStatusText()}
          </div>
        </div>
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Online Users</h3>
          <div className="text-sm text-gray-600 dark:text-gray-300">
            {isConnected ? '👤 You' : 'Waiting for connection...'}
          </div>
        </div>
      </div>
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">General Chat</h1>
            <div className={`text-sm ${getConnectionStatusColor()}`}>
              {getConnectionStatusText()}
            </div>
          </div>
        </div>
        
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
              {isConnected ? (
                <>
                  <p className="text-lg mb-2">👋 Welcome to Polylog!</p>
                  <p className="mb-1">Start a conversation by typing a message below.</p>
                  <p className="text-sm opacity-75">🤖 AI Assistant will respond to your messages!</p>
                </>
              ) : (
                <>
                  <p className="text-lg mb-2">🔌 Connecting...</p>
                  <p>Please wait while we establish the connection.</p>
                </>
              )}
            </div>
          ) : (
            messages.map((msg, index) => (
              <div 
                key={msg.id || index} 
                className={`flex ${
                  msg.userName === 'Test User' ? 'justify-end' : 'justify-start'
                } mb-4`}
              >
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.userName === 'System'
                    ? 'bg-gray-500 text-white' 
                    : msg.userName === 'AI Assistant'
                    ? 'bg-blue-500 text-white'
                    : msg.userName === 'Test User'
                    ? 'bg-green-500 text-white ml-auto'
                    : 'bg-purple-500 text-white'
                }`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium">
                      {msg.userName === 'System' ? '⚙️' : 
                       msg.userName === 'AI Assistant' ? '🤖' : 
                       msg.userName === 'Test User' ? '👤' : '💬'} {msg.userName}
                    </span>
                    <span className="text-xs opacity-75">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm">{msg.content}</p>
                </div>
              </div>
            ))
          )}
        </div>
        
        {/* Message Input */}
        <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder={isConnected ? "Type a message..." : "Waiting for connection..."}
              className={`flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                !isConnected ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={!isConnected}
            />
            <button
              className={`px-6 py-2 rounded-lg transition-colors ${
                isConnected && newMessage.trim()
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'bg-gray-400 text-gray-200 cursor-not-allowed'
              }`}
              onClick={handleSendMessage}
              disabled={!isConnected || !newMessage.trim()}
            >
              Send
            </button>
          </div>
          {!isConnected && (
            <p className="text-sm text-gray-500 mt-2">
              {connectionStatus === 'connecting' 
                ? 'Connecting to chat server...' 
                : 'Connection lost. Attempting to reconnect...'
              }
            </p>
          )}
        </div>
      </div>
    </div>
  );
}