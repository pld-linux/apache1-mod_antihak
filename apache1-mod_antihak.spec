%define apxs	/usr/sbin/apxs1
%define	mod_name	antihak
%define		tar_ver	0.3.1-beta
Summary:	Antihak module for Apache
Summary(pl):	Modu³ antihak dla Apache
Name:		apache1-mod_%{mod_name}
Version:	0.3.1beta
Release:	3.3
License:	GPL
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/apantihak/mod_antihak-%{tar_ver}.tar.gz
# Source0-md5:	38f22f5b5662e8dd7318c42fa96fb083
Patch0:		%{name}-iptables.patch
Patch1:		%{name}-am.patch
Patch2:		%{name}-mysql-API.patch
URL:		http://sourceforge.net/projects/apantihak/
BuildRequires:	%{apxs}
BuildRequires:	apache1-devel >= 1.3.33-2
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	mysql-devel
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	grep
Requires(preun):	sed >= 4.0
Requires:	apache1 >= 1.3.33-2
Requires:	iptables
Requires:	sudo
Obsoletes:	apache-mod_antihak <= %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
mod_antihak is an Apache Module designed to eliminate the CodeRed and
Nimda worm's network bandwidth consumption. We're working to make it
as easy as writing a line of text to add more worms! :)

%description -l pl
mod_antihak to modu³ Apache s³u¿±cy do eliminowania zapychania sieci
przez robaki CodeRed i Nimda. Ponadto trwaj± prace nad umo¿liwieniem
³atwego dodawania obs³ugi kolejnych robaków.

%prep
%setup -q -n mod_antihak-0.3.1-beta/src
%patch0 -p0
%patch1 -p0
%patch2 -p1

%build
rm -f tools/missing
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}

%configure \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -I/usr/include/mysql" \
	APACHE_APXS=%{apxs} \
	--with-mysql

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/conf.d}

install mod_antihak/mod_antihak.so $RPM_BUILD_ROOT%{_pkglibdir}
echo 'LoadModule %{mod_name}_module	modules/mod_%{mod_name}.so' > \
	$RPM_BUILD_ROOT%{_sysconfdir}/conf.d/90_mod_%{mod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if ! grep -qF "http ALL= NOPASSWD: /sbin/iptables" ; then
	echo "#http ALL= NOPASSWD: /sbin/iptables" >> /etc/sudoers
	echo "%{mod_name}: You need to allow apache to run iptables as root,"
	echo "%{mod_name}: appropriate (commented out) line added to /etc/sudoers;"
	echo "%{mod_name}: be sure to uncomment it if you want this module to work."
fi
%service -q apache restart

%postun
if [ "$1" = "0" ]; then
	if grep -qF "^http ALL= NOPASSWD: /sbin/iptables" /etc/sudoers ; then
		sed -i -e '/^http ALL= NOPASSWD: /sbin/iptables$/d' /etc/sudoers
	fi
	%service -q apache restart
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS INSTALL ChangeLog NEWS TODO
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*
