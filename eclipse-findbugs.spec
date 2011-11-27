%global eclipse_base %{_libdir}/eclipse
%global pkg_date     20090821

Name:           eclipse-findbugs
Version:        1.3.9
Release:        5
Summary:        Eclipse plugin for FindBugs

Group:          Development/Java
License:        LGPLv2+
URL:            http://findbugs.sourceforge.net/
Source0:        http://downloads.sourceforge.net/findbugs/eclipsePlugin-%{version}.%{pkg_date}-source.zip
# This patch is Fedora-specific, so it has not been submitted upstream.  The
# patch makes the build infrastructure use installed JARs for the build, rather
# than downloading JARs.
Patch0:         eclipsePlugin-%{version}-build.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  ant, ant-findbugs, eclipse-pde, findbugs
BuildRequires:  java-1.6.0-openjdk-devel, jpackage-utils
Requires:       ant, ant-findbugs, eclipse-jdt, findbugs
Requires:       java-1.6.0-openjdk, jpackage-utils

BuildArch:      noarch

%global plugins_dir %{_datadir}/eclipse/dropins/findbugs/plugins
%global plugin_dir  %{plugins_dir}/edu.umd.cs.findbugs.plugin.eclipse_%{version}.%{pkg_date}

%description
An Eclipse plugin for the FindBugs Java bug detector.

%prep
%setup -q -n eclipsePlugin-%{version}.%{pkg_date}
%patch0 -p1

# Set up the eclipse path
sed -i -e 's|@SWT_JAR@|%{eclipse_base}/swt.jar|' build.xml

# Make sure we don't use retroweaver
rm -fr tools

%build
ant -DeclipsePlugin.dir=%{eclipse_base}/plugins \
    -DeclipseJdtPlugin.dir=%{eclipse_base}/dropins/jdt/plugins \
    -DeclipseSdkPlugin.dir=%{eclipse_base}/dropins/sdk/plugins \
    -Dplugin.date=%{pkg_date} \
    -Drelease.base=%{version} \
    -Dfindbugs.dir=`pwd`

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{plugins_dir}
unzip -q -d $RPM_BUILD_ROOT%{plugins_dir} \
  bin_build/edu.umd.cs.findbugs.plugin.eclipse_%{version}.%{pkg_date}.zip

# Symlink to the external jars we need
%define javalink ../../../../../java
ln -s %{javalink}/ant.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/ant/ant-findbugs.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/commons-lang.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/dom4j.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/findbugs-bcel.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/findbugs.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/jaxen.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/jcip-annotations.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/jFormatString.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/jsr-305.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/objectweb-asm/asm-tree.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/objectweb-asm/asm.jar $RPM_BUILD_ROOT%{plugin_dir}
ln -s %{javalink}/objectweb-asm/asm-commons.jar $RPM_BUILD_ROOT%{plugin_dir}

# Remove unnecessary files (used at build-time only)
rm -f $RPM_BUILD_ROOT%{plugin_dir}/.options
rm -fr $RPM_BUILD_ROOT%{plugin_dir}/doc

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc RELEASENOTES
%{plugin_dir}

